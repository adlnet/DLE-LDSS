from django.db import models #Import Models and transaction atomic
from neomodel import db, StringProperty, DateTimeProperty, BooleanProperty, RelationshipTo, RelationshipFrom, StructuredNode, IntegerProperty, NodeSet
import time
import logging
import re
from django_neomodel import DjangoNode
from uuid import uuid4

logger = logging.getLogger(__name__)

GLOBAL_PROVIDER_OWNER_UID = "0xFFFFFFFF"
UID_PATTERN = r"^0x[0-9A-Fa-f]{8}$"
COLLISION_THRESHOLD = 5 


# Generated Logs to track instance, time of generation, uid, provider and lcv terms
class GeneratedUIDLog(models.Model):
    uid = models.CharField(max_length=255, default="UNKNOWN")
    uid_full = models.CharField(max_length=255, default="UNKNOWN")
    generated_at = models.DateTimeField(auto_now_add=True)
    generator_id = models.CharField(max_length=255)
    provider = models.CharField(max_length=255, blank=True)
    lcv_terms = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Generated UID Log"
        verbose_name_plural = "Generated UID Logs"

class UIDCounter(StructuredNode):
    owner_uid = StringProperty(required=True)
    counter = IntegerProperty(default=0)
    
    @classmethod
    def get_instance(cls, owner_uid: str) -> 'UIDCounter':
        nodes = UIDCounter.nodes
        result = nodes.get_or_none(owner_uid=owner_uid)

        if result is None:
            instance = UIDCounter(owner_uid=owner_uid)
            instance.save()
            return instance
        
        if isinstance(result, list):
            instance = result[0]
        else:
            instance = result
        
        assert isinstance(instance, UIDCounter)
        return instance 

    @classmethod
    def increment(cls, owner_uid: str):
        instance = cls.get_instance(owner_uid)
        current_value = instance.counter
        instance.counter = current_value + 1
        instance.save()
        return instance.counter

# UID Compliance check
def is_uid_compliant(uid):
    """Check if the UID complies with the specified pattern."""
    return bool(re.match(UID_PATTERN, uid))

def report_malformed_uids():
    """Generate a report of all malformed UIDs."""
    malformed_uids = []
    logs = GeneratedUIDLog.objects.all()
    
    for log in logs:
        if not is_uid_compliant(log.uid):
            malformed_uids.append(log.uid)
    
    return malformed_uids


# Neo4j UID Node
class UIDNode(DjangoNode):
    uid = StringProperty(required=True)
    updated_at = DateTimeProperty(default_now=True)
    created_at = DateTimeProperty(default_now=True)

    @classmethod
    def get_node_by_uid(cls, uid: str):
        return cls.nodes.get_or_none(uid=uid)
    
    @classmethod
    def create_node(cls, owner_uid: str) -> 'UIDNode':
        uid_value = generate_uid(owner_uid)
        uid_node = cls(uid=uid_value)
        uid_node.save()
        return uid_node
    
    class Meta:
        app_label = 'uid'


# Refactored UID Generator that manages both Neo4j and DjangoNode and confirms Neo4j is available
def generate_uid(owner_uid) -> str:

    uid_value = UIDCounter.increment(owner_uid=owner_uid)
    attempts = 0 # Initialize attempts here change as needed
    
    while True:
        new_uid = f"0x{uid_value:08x}"
        
        # Collision threshold, if too many attempts, break, reset attempts and increment base counter
        if attempts >= COLLISION_THRESHOLD:
            logger.error(f"Too many collisions for base UID {uid_value}. Incrementing counter.")
            attempts = 0
            break
        
        logger.info(f"Adjusted UID to {new_uid} to resolve collision.")
    
        # Compliance check
        if not is_uid_compliant(new_uid):
            logger.error(f"Generated UID {new_uid} is not compliant with the expected pattern.")
            continue
        
        uid_full = f"{owner_uid}-{new_uid}"
        GeneratedUIDLog.objects.create(uid=new_uid, uid_full=uid_full)

        return new_uid
    
    raise ValueError(f"COULD NOT GENERATE A NEW UID FOR OWNER: {owner_uid}")

# Provider and LCVTerms now Nodes
class Provider(DjangoNode):
    name = StringProperty(required=True, unique=True)
    default_uid = StringProperty(required=True)

    uid = RelationshipTo('UIDNode', 'HAS_UID')
    uid_counter = RelationshipTo('UIDCounter', 'HAS_UID_COUNTER')

    class Meta:
        app_label = 'uid'

    @classmethod
    def create_provider(cls, name) -> 'Provider':
        
        uid_node = UIDNode.create_node(owner_uid=GLOBAL_PROVIDER_OWNER_UID)
        counter_node = UIDCounter.get_instance(owner_uid=uid_node.uid)

        provider = Provider(name=name, default_uid=uid_node.uid)
        provider.save()
        provider.uid.connect(uid_node)
        provider.uid_counter.connect(counter_node)
        provider.save()

        return provider
    
    @classmethod
    def does_provider_exist(cls, name):
        provider_nodes = Provider.nodes
        assert isinstance(provider_nodes, NodeSet)
        result = provider_nodes.get_or_none(name=name)

        return result is not None
    
    @classmethod
    def get_provider_by_name(cls, name):
        provider_nodes = Provider.nodes
        assert isinstance(provider_nodes, NodeSet)
        result = provider_nodes.get_or_none(name=name)

        if result is None:
            raise ValueError(f"CANNOT FIND REQUESTED PROVIDER: {name}")

        provider = result
        if isinstance(provider, list):
            provider = result[0]

        assert isinstance(provider, Provider)
        return provider
    
    def get_current_uid(self):
        current_uid = self.default_uid

        current_uid_node = self.uid.end_node()
        if current_uid_node is not None:
            assert isinstance(current_uid_node, UIDNode)
            current_uid = current_uid_node.uid

        return current_uid

# Django Provider Model for Admin
class ProviderDjangoModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    @classmethod
    def does_django_provider_exist(cls, provider_name: str):
        result = ProviderDjangoModel.objects.filter(name=provider_name).first()
        return result is not None
    
    @classmethod
    def ensure_provider_exists(cls, provider_name: str) -> 'Provider':
        """
        Ensure that this Provider exists as both a Django Model (for the admin view)
        and as a graph node.  The graph node portion is handled by the save() override,
        which gives that node as an extended return value.
        """
        django_provider, created = ProviderDjangoModel.objects.get_or_create(name=provider_name)
        
        if not Provider.does_provider_exist(provider_name):
            provider = Provider.create_provider(provider_name)
        else:
            provider = Provider.get_provider_by_name(provider_name)
        
        return provider

    @classmethod
    def get_by_name(cls, provider_name: str):
        return ProviderDjangoModel.objects.get(name=provider_name)

    def save(self, *args, **kwargs) -> 'Provider':
        # Create or update the Neo4j Provider node  
        if not Provider.does_provider_exist(self.name):
            provider = Provider.create_provider(self.name)
        else:
            provider = Provider.get_provider_by_name(self.name)
        super().save(*args, **kwargs)
        return provider

    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"

class UIDRequestToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    provider_name = models.CharField(max_length=255)
    echelon = models.CharField(max_length=255)
    termset = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    uid_chain = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        
        given_provider = self.provider_name
        
        requested_node = UIDRequestNode.create_requested_uid(given_provider)
        requested_node.save()

        self.token = requested_node.token
        self.uid = requested_node.default_uid
        self.uid_chain = requested_node.default_uid_chain

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "UIDRequestToken"
        verbose_name_plural = "UIDRequestTokens"

class UIDRequestNode(DjangoNode):
    token = StringProperty(required=True)
    default_uid = StringProperty(required=True)
    default_uid_chain = StringProperty(default="")

    provider = RelationshipTo('Provider', 'HAS_PROVIDER')
    uid = RelationshipTo('UIDNode', 'HAS_UID')

    @classmethod
    def create_requested_uid(cls, provider_name: str):
        
        provider = ProviderDjangoModel.ensure_provider_exists(provider_name)
        assert isinstance(provider, Provider)
                
        uid_node = UIDNode.create_node(owner_uid=provider.default_uid)

        requested_node = UIDRequestNode()
        requested_node.token = uuid4()
        requested_node.default_uid = uid_node.uid
        requested_node.default_uid_chain = f"{provider.default_uid}-{uid_node.uid}" 
        requested_node.save()
        requested_node.uid.connect(uid_node)
        requested_node.provider.connect(provider)
        requested_node.save()
        
        return requested_node

# Adding reporting by echelon level
def report_uids_by_echelon(echelon_level):
    """Retrieve UIDs issued at a specific echelon level."""
    nodes = UIDNode.nodes
    assert isinstance(nodes, NodeSet)
    nodes = nodes.filter(echelon_level=echelon_level)
    return [node.uid for node in nodes]

def report_all_uids():
    """Retrieve all UIDs issued in the enterprise."""
    nodes = UIDNode.nodes.all()
    return [node.uid for node in nodes]

# Reporting function for all generated UIDs
def report_all_generated_uids():
    """Retrieve all generated UIDs from the log."""
    logs = GeneratedUIDLog.objects.all()
    return [
        {
            "uid": log.uid, 
            "uid_full": log.uid_full, 
            "generated_at": str(log.generated_at)
        } for log in logs
    ]
