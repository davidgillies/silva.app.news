#
# SilvaTestCase
#

__version__ = '0.3.0'

from Testing import ZopeTestCase

_user_name = ZopeTestCase._user_name
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
ZopeTestCase.installProduct('SilvaDocument')
ZopeTestCase.installProduct('Silva')
ZopeTestCase.installProduct('SilvaFunctionalTests')
ZopeTestCase.installProduct('SilvaNews')

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time

class SilvaTestCase(ZopeTestCase.ZopeTestCase):

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
                ZopeTestCase._user_name)
                
            self.afterSetUp()
        except:
            self._clear()
            raise
        
    def _setupRootUser(self):
        '''Creates the root user.'''
        uf = self.root.acl_users
        uf._doAddUser(_user_name, 'secret', ['ChiefEditor'], [])
        
    def addObject(self, container, type_name, id, product='Silva',
            **kw):
        getattr(container.manage_addProduct[product],
            'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        get_transaction().commit(1)
        return getattr(container, id)

    # Security interfaces

    def setRoles(self, roles, name=_user_name):
        '''Changes the roles assigned to a user.'''
        uf = self.root.acl_users
        uf._doChangeUser(name, None, roles, []) 
        if name == getSecurityManager().getUser().getId():
            self.login(name)

    def setPermissions(self, permissions, role='Member'):
        '''Changes the permissions assigned to a role.
        '''
        self.root.manage_role(role, permissions)

    def installExtension(self, extension):
        """Installs a Silva extension""" 
        ZopeTestCase.installProduct(extension)
        self.getRoot().service_extensions.install(extension)

    def login(self, name=_user_name):
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
        get_transaction().commit()
        if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

# Create a Silva site in the test (demo-) storage
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.utils.setupCoreSessions(app)
setupSilvaRoot(app, id='root')
ZopeTestCase.close(app)

