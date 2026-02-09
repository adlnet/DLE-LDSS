import logging
import os
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django_neomodel import DjangoNode
from uid.models import UIDNode, ProviderDjangoModel
from neomodel import StringProperty, BooleanProperty, RelationshipTo, RelationshipFrom, UniqueIdProperty, ArrayProperty, exceptions, FloatProperty, Relationship, IntegerProperty
from typing import Tuple

logger = logging.getLogger('dict_config_logger')

data_type_matching = {
    'str': 'schema:Text',
    'int': 'schema:Number',
    'bool': 'schema:Boolean',
    'datetime': 'schema:DateTime'
}
regex_check = (r'(?!(\A( \x09\x0A\x0D\x20-\x7E # ASCII '
               r'| \xC2-\xDF # non-overlong 2-byte '
               r'| \xE0\xA0-\xBF # excluding overlongs '
               r'| \xE1-\xEC\xEE\xEF{2} # straight 3-byte '
               r'| \xED\x80-\x9F # excluding surrogates '
               r'| \xF0\x90-\xBF{2} # planes 1-3 '
               r'| \xF1-\xF3{3} # planes 4-15 '
               r'| \xF4\x80-\x8F{2} # plane 16 )*\Z))')

ldss_const = "ldss:"


def validate_version(value):
    check = re.fullmatch(r'\d*\.\d*\.\d*', value)
    if check is None:
        raise ValidationError(
            '%(value)s does not match the format 0.0.0',
            params={'value': value},
        )

class NeoTerm(DjangoNode):
    django_id = UniqueIdProperty()
    uid = StringProperty(unique_index=True)
    uid_chain = StringProperty(unique_index=True)
    lcvid = StringProperty()
    status = StringProperty(choices={'accepted':'accepted', 'rejected':'rejected', 'pending':'pending'}, default='pending')
    term = StringProperty(default="UNASSIGNED")
    deprecated = BooleanProperty(default=False)
    uid_node = RelationshipTo('UIDNode', 'HAS_UID')
    definition = RelationshipTo('NeoDefinition', 'POINTS_TO')
    context = RelationshipFrom('NeoContext', 'IS_A')
    alias = RelationshipFrom('NeoAlias', 'POINTS_TO')
    mapping_node = Relationship('NeoMapping', 'MAPS_TO')

    class Meta:
        app_label = 'core'

    @classmethod
    def create_new_term(cls, lcvid: str = None) -> 'NeoTerm':

        term_node = NeoTerm() if lcvid is None else NeoTerm(lcvid=lcvid)
        term_uid_node = UIDNode.create_node(term_node.lcvid)
        term_node.uid = term_uid_node.uid
        term_node.save()

        term_node.uid_node.connect(term_uid_node)
        term_node.save()

        default_provider_name = term_node.lcvid
        provider = ProviderDjangoModel.ensure_provider_exists(default_provider_name)

        provider.uid.connect(term_uid_node)
        provider.save()

        term_node.uid_chain = f"{lcvid}-{provider.default_uid}-{term_node.uid}"
        term_node.save()

        return term_node

    @classmethod
    def get_by_uid(cls, uid: str) -> 'NeoTerm':
        try:
            node = cls.nodes.get(uid=uid)

            if node is None:
                return None

            return node

        except exceptions.MultipleNodesReturned as e:
            logger.error("Multiple nodes found with uid '%s': %s", uid, e)
            raise ValidationError(f"Multiple nodes found with uid '{uid}. Expected only one.") from e

        except exceptions.DoesNotExist as e:
            logger.error("NeoModel-related error while getting term '%s': %s", uid, e)
            raise e
        
        except Exception as e:
            logger.error("Unexpected error while getting term '%s': %s", uid, e)
            raise ValidationError(f"Unexpected error while getting term '{uid}': {e}") from e

    def set_relationships(self, definition_node=None, context_node=None, alias_node=None):
        try:
            if alias_node:
                self.alias.connect(alias_node)
            if context_node:
                self.context.connect(context_node)
            if definition_node:
                self.definition.connect(definition_node)
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while connecting relationships for term %s, %s", self.uid, e)
            raise e

    def to_json(self):
        try:
            definition_node = self.definition.single()
            return {
                "uid": self.uid,
                "uid_chain": self.uid_chain,
                "lcvid": self.lcvid,
                "status": self.status,
                "deprecated": self.deprecated,
                "definition": definition_node.definition if definition_node else None,
            }
        except Exception as e:
            logger.error("Error while converting NeoTerm to json: %s", e)
        
        return None

class NeoAlias(DjangoNode):
    django_id = UniqueIdProperty()
    alias = StringProperty(unique_index=True,required=True)
    term = RelationshipTo('NeoTerm', 'POINTS_TO')
    context = RelationshipTo('NeoContext', 'USED_IN')
    collided_definition = Relationship('NeoDefinition', 'WAS_ADDED_WITH')
    class Meta:
        app_label = 'core'

    @classmethod
    def get_or_create(cls, alias: str) -> Tuple['NeoAlias', bool]:
        """Retrieve an existing NeoAlias or create a new one if not found, with error handling."""
        try:
            alias_node = cls.nodes.get_or_none(alias=alias)

            if alias_node:
                return alias_node, False

            alias_node = NeoAlias(alias=alias)
            alias_node.save()
            return alias_node, True

        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while getting or creating alias %s: %s", alias, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error in get_or_create for alias %s: %s", alias, e)
            raise e

    def set_relationships(self, term_node=None, context_node=None, collided_definition=None):
        try:
            if term_node:
                self.term.connect(term_node)
            if context_node:
                self.context.connect(context_node)
            if collided_definition:
                self.collided_definition.connect(collided_definition)
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while connecting relationships for alias %s: %s", self.alias, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error while connecting relationships for alias %s: %s",self.alias, e)
            raise e

    def handle_collision(self, definition_node, context_node=None):
        if context_node:
            self.context.connect(context_node)
        self.collided_definition.connect(definition_node)

class NeoContext(DjangoNode):
    django_id = UniqueIdProperty()
    context = StringProperty(unique_index = True)
    context_description = RelationshipFrom('NeoContextDescription', 'RATIONALE')
    term = RelationshipTo('NeoTerm', 'IS_A')
    alias = RelationshipFrom('NeoAlias', 'USED_IN')
    definition = RelationshipFrom('NeoDefinition', 'VALID_IN' )

    class Meta:
        app_label = 'core'

    @classmethod
    def get_or_create(cls, context: str) -> Tuple['NeoContext', bool]:
        if context == "":
            raise ValueError(f"Could not get or create the requested context node w/ context: {context}")
        try:
            context_node = cls.nodes.get_or_none(context=context)
            if context_node:
                return context_node, False
            context_node = NeoContext(context=context)
            context_node.save()
            return context_node, True
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while getting or creating context %s: %s", context, e)
            raise e
        
        except Exception as e:
            logger.error("Unexpected error in get_or_create for context %s: %s", context, e)
            raise e

    def set_relationships(self, term_node=None, alias_node=None, definition_node=None, context_description_node=None,):
        try:
            if term_node:
                self.term.connect(term_node)
            if alias_node:
                self.alias.connect(alias_node)
            if definition_node:
                self.definition.connect(definition_node)
            if context_description_node:
                self.context_description.connect(context_description_node)
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while connecting relationships for context %s: %s", self.context, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error while connecting relationships for context %s: %s",self.context, e)
            raise e


class NeoContextDescription(DjangoNode):
    context_description = StringProperty(required=True)
    definition = RelationshipTo('NeoDefinition', 'BASED_ON')
    context = RelationshipTo('NeoContext', 'RATIONALE')

    class Meta:
        app_label = 'core'

    @classmethod
    def get_or_create(cls, context_description: str, context_node: 'NeoContext'):
        try:
            existing = context_node.context_description.all() if context_node else []
            if existing:
                return existing[0], False
            context_description_node = cls(context_description=context_description)
            context_description_node.save()
            return context_description_node, True
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while getting or creating context_description %s: %s", context_description, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error in get_or_create for context_description %s: %s", context_description, e)
            raise e

    def set_relationships(self, definition_node=None, context_node=None):
        try:
            if definition_node:
                self.definition.connect(definition_node)
            if context_node:
                self.context.connect(context_node)
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while connecting relationships for context_description %s: %s", self.context_description, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error while connecting relationships for context_description %s: %s", self.context_description, e)
            raise e

class NeoDefinition(DjangoNode):
    django_id = UniqueIdProperty()
    entity_id = StringProperty(required=True)
    definition = StringProperty(required=True)
    embedding = ArrayProperty(FloatProperty(), required=False)
    rejected = BooleanProperty(default=False)
    context = RelationshipTo('NeoContext', 'VALID_IN')
    context_description = RelationshipFrom('NeoContextDescription', 'BASED_ON')
    term = Relationship('NeoTerm', 'POINTS_TO')
    collision = Relationship('NeoDefinition', 'IS_COLLIDING_WITH')
    collision_alias = Relationship('NeoAlias', 'WAS_ADDED_WITH')

    class Meta:
        app_label = 'core'

    @classmethod
    def get_or_create(cls, definition:str, entity_id: str, definition_embedding=None):
        try:
            definition_node = cls.nodes.get_or_none(definition=definition, entity_id=entity_id)
            if definition_node:
                return definition_node, False
            definition_node = NeoDefinition(definition=definition, entity_id=entity_id, embedding=definition_embedding)
            definition_node.save()
            return definition_node, True

        except Exception as e:
            logger.error("Error in get for NeoDefinition %s: %s", definition, e)
            raise e

    @classmethod
    def get_by_definition(cls, definition:str):
        try:
            return cls.nodes.get(definition=definition)
        except exceptions.DoesNotExist as e:
            logger.error("NeoModel-related error while getting definition %s: %s", definition, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error while getting definition %s: %s", definition, e)
            raise e

    def get_term_node(self)-> 'NeoTerm':
        try:
            if self.term:
                return self.term.single()
            return None
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while getting term node for definition %s: %s", self.definition, e)
            raise e

    def set_relationships(self, term_node=None, context_node=None, context_description_node=None, collision=None, collision_alias=None):
        try:
            if term_node:
                self.term.connect(term_node)
            if context_node:
                self.context.connect(context_node)
            if context_description_node:
                self.context_description.connect(context_description_node)
            if collision:
                self.collision.connect(collision)
            if collision_alias:
                self.collision_alias.connect(collision_alias)
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while connecting relationships for definition %s: %s", self.definition, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error while connecting relationships for definition %s: %s", self.definition, e)
            raise e

class NeoMapping(DjangoNode):
    uid_chain = StringProperty()
    lcvid = StringProperty()
    lcv_downstream_id = IntegerProperty()
    uid = StringProperty()
    definition = StringProperty()
    aliases = ArrayProperty(StringProperty(), required=False)
    definition_embedding = ArrayProperty(FloatProperty(), required=False)
    contexts = ArrayProperty(StringProperty(), required=False)
    neoterm_node = RelationshipTo('NeoTerm', 'MAPS_TO')

    class Meta:
        app_label = 'core'

    @classmethod
    def create_node(cls, uid_chain: str, lcvid: str, uid: str, definition: str, aliases=None ,definition_embedding=None, lcv_downstream_id=None) -> 'NeoMapping':
        try:
            mapping_node = NeoMapping(uid_chain=uid_chain, lcvid=lcvid, uid=uid, aliases=aliases,definition=definition, definition_embedding=definition_embedding)
            mapping_node.save()
            return mapping_node
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while creating mapping %s: %s", lcvid, {e})
            raise e
        except Exception as e:
            logger.error("Unexpected error while creating mapping %s: %s", lcvid, {e})
            raise e
        
    @classmethod
    def get_node(cls, uid_chain: str, uid: str) -> 'NeoMapping':
        try:
            return NeoMapping.nodes.get(uid_chain=uid_chain, uid=uid)
        except exceptions.DoesNotExist as e:
            logger.error("NeoModel-related error while getting mapping %s %s", uid_chain, e)
            raise e
        except Exception as e:
            logger.error("Unexpected error while getting mapping %s %s", uid_chain, e)
            raise e

    def set_relationships(self, term_node: 'NeoTerm'):
        try:
            if term_node:
                self.neoterm_node.connect(term_node)
                self.save()
            else:
                raise ValueError("neoterm_node is None")
        except exceptions.NeomodelException as e:
            logger.error("NeoModel-related error while connecting relationships for mapping '%s to neoterm %s': %s", self.lcvid, term_node.uid, e)
            raise e
