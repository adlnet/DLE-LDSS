import json

import requests
from requests.auth import AuthBase

from configurations.models import CourseInformationMapping, XMSConfigurations


# helper function to get the catalogs from XIS
def get_xis_catalogs():
    """Get all the catalogs available in the XIS

    Returns:
        requests.Response: [dictionary]
    """

    # get the XMS configuration for the XIS catalog host
    xis_catalogs_url = (
        XMSConfigurations.objects.first().target_xis_host
    )

    # request the catalogs from the XIS
    return requests.get(xis_catalogs_url)


# helper function to get an experience from XIS
def get_xis_experience(provider_id, experience_id):
    """
    Get a specific experience from a specific catalog

    Args:
        provider_id (string): the query parameter for the catalog
        experience_id (strint): the metadata_key_hash for the experience

    Returns:
        requests.Response: [dictionary]

    Note:
        Only returns one experience in an array if successful
    """

    # get the XIS host from the configuration
    xis_metadata_experience_url = (
        XMSConfigurations.objects.first().target_xis_host
    )

    # construct the url for the experience
    xis_metadata_experience_url = (
        xis_metadata_experience_url
        + f"/{provider_id}/{experience_id}"
    )

    return requests.get(xis_metadata_experience_url)


# helper function to post an experience from XIS
def post_xis_experience(data, provider_id, experience_id):
    """
    Post a specific experience from a specific catalog

    Args:
        provider_id (string): the query parameter for the catalog
        experience_id (string): the metadata_key_hash for the experience

    Returns:
        requests.Response: [dictionary]

    Note:
        Only returns one experience in an array if successful
    """

    # get the XIS host from the configuration
    xis_metadata_experience_url = (
        XMSConfigurations.objects.first().target_xis_host
    )

    # construct the url for the experience
    xis_metadata_experience_url = (
        xis_metadata_experience_url
        + f"/{provider_id}/{experience_id}"
    )

    # formatting the request data to JSON
    dataJSON = json.dumps(data)

    headers = {'content-type': 'application/json'}

    return requests.post(xis_metadata_experience_url, data=dataJSON,
                         timeout=30, headers=headers, auth=TokenAuth())


# helper function to get all experiences from a catalog in XIS
def get_catalog_experiences(provider_id, page, search, page_size):
    """Get all the experiences for a given catalog

    Args:
        provider_id (string): the query parameter for the catalog
        search (string): the query parameter for the search
        page (int): the query parameter for the page number
    Returns:
        requests.Response: [dictionary]
    """
    xis_metadata_url = (
        XMSConfigurations.objects.first().target_xis_host
    )
    xis_metadata_url = xis_metadata_url + f"/{provider_id}"
    search_fields = CourseInformationMapping.objects.first().list_fields()

    # request the experiences from the specified catalog
    return requests.get(xis_metadata_url, params={'page': page,
                                                  'search': search,
                                                  'page_size': page_size,
                                                  'fields':
                                                  ','.join(search_fields)})


class TokenAuth(AuthBase):
    """Attaches HTTP Authorization Header to the given Request object."""

    def __call__(self, r, token_name='token'):
        # modify and return the request

        r.headers['Authorization'] = token_name + ' ' + \
            XMSConfigurations.objects.first().xis_api_key
        return r
