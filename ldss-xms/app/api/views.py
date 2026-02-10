import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils.xis_helper_functions import (get_catalog_experiences,
                                            get_xis_catalogs,
                                            get_xis_experience,
                                            post_xis_experience)
from configurations.models import CatalogConfigurations

generic_error = "There was an error processing your request."
bad_user = "Missing user credentials or catalog access"
wrong_provider = "The provider id does not exist in the XIS catalogs"


class XISAvailableCatalogs(APIView):
    """Catalog List View"""

    def get(self, request) -> Response:
        """Returns the list of catalogs found in the current user"""

        # get the url for the XIS catalogs
        xis_catalogs_response = get_xis_catalogs()

        # check if the request was successful
        if xis_catalogs_response.status_code == 200:
            for catalog in json.loads(xis_catalogs_response.json()):
                if not CatalogConfigurations.objects.filter(name=catalog)\
                        .exists():
                    CatalogConfigurations(name=catalog).save()

        # return the response
        return Response(json.dumps([str(catalog) for catalog in
                                    request.user.catalogs.all()]),
                        status.HTTP_200_OK)


class XISCatalog(APIView):
    """Catalog View"""

    def get(self, request, provider_id) -> Response:
        """Returns all the courses in the corresponding catalog

        Args:
            provider_id (string): the query parameter for the catalog
        """

        # get the available catalog data
        xis_catalogs_response = get_xis_catalogs()

        # check if the request was successful (GET)
        if xis_catalogs_response.status_code != 200:
            # return the error message
            return Response(
                {"detail": generic_error},
                status=xis_catalogs_response.status_code,
            )

        # validate that the provider_id is valid
        if provider_id not in xis_catalogs_response.json():
            return Response(
                {
                    "detail": wrong_provider
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # validate the user should be able to view the catalog
        if not request.user.is_authenticated or not\
                request.user.catalogs.filter(name=provider_id).exists():
            return Response(
                {
                    "detail": bad_user
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        page = request.GET.get('page')
        search = request.GET.get('search')
        page_size = request.GET.get('page_size')

        # get the experiences data for the catalog provided
        provider_catalog_response = \
            get_catalog_experiences(provider_id, page, search, page_size)

        # check if the request was successful (GET)
        if provider_catalog_response.status_code != 200:
            # return the error message
            return Response(
                {"detail": generic_error},
                status=provider_catalog_response.status_code,
            )

        # grab the experiences json
        catalog_experiences_list = provider_catalog_response.json()

        return Response(
            {
                "experiences": catalog_experiences_list,
            },
            status=status.HTTP_200_OK,
        )


class XISExperience(APIView):
    """Experience from a specific catalog"""

    def get(self, request, provider_id, experience_id) -> Response:
        """Returns the experience from the corresponding catalog

        Args:
            provider_id (string): the query parameter for the catalog
            experience_id (string): the metadata_key_hash for the experience
        """

        xis_catalogs_response = get_xis_catalogs()

        # check if the request was successful
        if xis_catalogs_response.status_code != 200:
            # return the error message
            return Response(
                {"detail": generic_error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # validate that the provider_id is valid
        if provider_id not in xis_catalogs_response.json():
            return Response(
                {
                    "detail": wrong_provider
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # validate the user should be able to view the catalog
        if not request.user.is_authenticated or not\
                request.user.catalogs.filter(name=provider_id).exists():
            return Response(
                {
                    "detail": bad_user
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        provider_experience_response = get_xis_experience(
            provider_id=provider_id, experience_id=experience_id
        )

        # check if the request was successful
        if provider_experience_response.status_code != 200:
            # return the error message
            return Response(
                {"detail": generic_error},
                status=provider_experience_response.status_code,
            )

        # grab the first experience returned in the response
        experience = provider_experience_response.json()[0]

        return Response(experience, status=status.HTTP_200_OK)

    def post(self, request, provider_id, experience_id) -> Response:
        """Returns the experience from the corresponding catalog

        Args:
            provider_id (string): the query parameter for the catalog
            experience_id (string): the metadata_key_hash for the experience
        """

        xis_catalogs_response = get_xis_catalogs()

        # check if the request was successful
        if xis_catalogs_response.status_code != 200:
            # return the error message
            return Response(
                {"detail": generic_error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # validate that the provider_id is valid
        if provider_id not in xis_catalogs_response.json():
            return Response(
                {
                    "detail": wrong_provider
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # validate the user should be able to view the catalog
        if not request.user.is_authenticated or not\
                request.user.catalogs.filter(name=provider_id).exists():
            return Response(
                {
                    "detail": bad_user
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        provider_experience_response = get_xis_experience(
            provider_id=provider_id, experience_id=experience_id
        )

        # check if the request was successful
        if provider_experience_response.status_code != 200:
            # return the error message
            return Response(
                {"detail": "The experience does not exist in the XIS "
                 "catalogs"},
                status=status.HTTP_404_NOT_FOUND,
            )

        provider_experience_update_response = \
            post_xis_experience(request.data, provider_id=provider_id,
                                experience_id=experience_id)

        # check if the request was successful
        if provider_experience_update_response.status_code // 10 != 20:
            # return the error message
            return Response(
                {"detail": generic_error},
                status=provider_experience_update_response.status_code,
            )

        # grab the first experience returned in the response
        experience = provider_experience_update_response.json()

        return Response(experience,
                        status=provider_experience_update_response.status_code)
