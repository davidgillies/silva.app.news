from Interface import Base

class INewsItem(Base):
    """Silva News Item interface
    """
    def creation_datetime(self):
        """Returns the time of creation
        """
        pass

    def to_xml(self, context):
        """Returns XML of the item"""
        pass
