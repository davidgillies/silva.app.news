#
# SilvaTestCase
#

__version__ = '0.3.0'

from Testing import ZopeTestCase
try: 				# post initial Silva 1.4 release
    from Products.Silva.transactions import transaction
except ImportError:
    try: 			# Zope 2.8 style transactions
        import transaction
    except ImportError: 	# Old-style transactions
        class BBBTransactionMan:
            def begin(self):              get_transaction().begin()
            def commit(self, sub=False):  get_transaction().commit(sub)
            def abort(self, sub=False):   get_transaction().abort(sub)
            def get(self):                return get_transaction()
        transaction = BBBTransactionMan()

user_name = ZopeTestCase.user_name
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TemporaryFolder')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('PageTemplates')
ZopeTestCase.installProduct('Formulator')
ZopeTestCase.installProduct('FileSystemSite')
ZopeTestCase.installProduct('ParsedXML')
ZopeTestCase.installProduct('XMLWidgets')
ZopeTestCase.installProduct('ProxyIndex')
ZopeTestCase.installProduct('SilvaMetadata')
ZopeTestCase.installProduct('SilvaViews')
ZopeTestCase.installProduct('SilvaExternalSources')
ZopeTestCase.installProduct('SilvaDocument')
ZopeTestCase.installProduct('Silva')
ZopeTestCase.installProduct('SilvaFunctionalTests')
ZopeTestCase.installProduct('SilvaNews')

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time

class SilvaTestCase(ZopeTestCase.ZopeTestCase):

    _configure_root = 1

    def getRoot(self):
        """Returns the silva root object, i.e. the "fixture root". 
           Override if you don't like the default.
        """
        return self.app.root

    def setUp(self):     
        '''Sets up the fixture. Do not override, 
           use the hooks instead.
        '''
        try:
            self.beforeSetUp()
            self.app = self._app()

            # configure Silva
            self.silva = self.root = self.getRoot()
            self.catalog = self.silva.service_catalog
            self._setupRootUser()
            self.login()
            self.app.REQUEST.AUTHENTICATED_USER=self.app.acl_users.getUser(
                ZopeTestCase.user_name)
                
            self.afterSetUp()
        except:
            self._clear()
            raise
        
    def _setupRootUser(self):
        '''Creates the root user.'''
        uf = self.root.acl_users
        uf._doAddUser(user_name, 'secret', ['ChiefEditor'], [])
        
    def addObject(self, container, type_name, id, product='Silva',
            **kw):
        getattr(container.manage_addProduct[product],
            'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        transaction.get().commit(1)
        return getattr(container, id)

    # Security interfaces

    def setRoles(self, roles, name=user_name):
        '''Changes the roles assigned to a user.'''
        uf = self.root.acl_users
        uf._doChangeUser(name, None, roles, []) 
        if name == getSecurityManager().getUser().getId():
            self.login(name)

    def setPermissions(self, permissions, role='Member', context=None):
        '''Changes the permissions assigned to a role.
           If context is None it defaults to the root
           object.
        '''
        if context is None:
            context = self.root
        context.manage_role(role, permissions)

    def installExtension(self, extension):
        """Installs a Silva extension""" 
        ZopeTestCase.installProduct(extension)
        self.getRoot().service_extensions.install(extension)

    def login(self, name=user_name):
        '''Logs in as the specified user.'''
        uf = self.root.acl_users
        user = uf.getUserById(name).__of__(uf)
        newSecurityManager(None, user)

    def logout(self):
        '''Logs out.'''
        noSecurityManager()

    def add_folder(self, object, id, title, **kw):
        return self.addObject(object, 'Folder', id, title=title, **kw)

    def add_publication(self, object, id, title, **kw):
        return self.addObject(object, 'Publication', id, title=title, **kw)

    def add_document(self, object, id, title):
        return self.addObject(object, 'Document', id, title=title,
                              product='SilvaDocument')

    def add_ghost(self, object, id, content_url):
        return self.addObject(object, 'Ghost', id, content_url=content_url)

    def add_link(self, object, id, title, url):
        return self.addObject(object, 'Link', id, title=title, url=url)
    
    def add_image(self, object, id, title, **kw):
        return self.addObject(object, 'Image', id, title=title, **kw)

def setupSilvaRoot(app, id='root', quiet=0):
    '''Creates a Silva root.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet:
            ZopeTestCase._print('Adding Silva Root... ')
        uf = app.acl_users
        uf._doAddUser('SilvaTestCase', '', ['Manager'], [])
        user = uf.getUserById('SilvaTestCase').__of__(uf)
        newSecurityManager(None, user)
#        factory = app.manage_addProduct['TemporaryFolder']
#        factory.constructTemporaryFolder('temp_folder', '')
        factory = app.manage_addProduct['Silva']
        factory.manage_addRoot(id, '')
        root = app.root

        # add test users and roles
        for role in ['Author', 'Editor', 'ChiefEditor', 'Manager']:
            uf._doAddUser('silva_%s' % role, 'secret', [], [])
            root.manage_addLocalRoles('silva_%s' % role, [role])

        # install SilvaNews
        from Products.SilvaNews.install import install
        install(root)
        
        noSecurityManager()
        transaction.commit()
        if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

# Create a Silva site in the test (demo-) storage
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.utils.setupCoreSessions(app)
setupSilvaRoot(app, id='root')
transaction.commit()
ZopeTestCase.close(app)
