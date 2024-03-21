class ISORequestor:
    """
    The ISORequestor class allows users to request items or services through
    the application, functioning similarly to current ISO management practices.
    Users can specify various details about the item or service they are seeking,
    including title, optional description, optional image, and the price they are
    willing to pay. These requests are then uploaded to the database for recording
    and tracking purposes.

    Once a transaction related to a request is successfully completed, the requester
    has the capability to mark this in their post. This action automatically updates
    the transaction's status as complete in the transaction history database, providing
    a record of the completed transaction.

    Attributes:
        title (str): The title of the item or service being requested.
        description (str, optional): A more detailed description of the item or service.
        image (Image, optional): An image representing the item or service.
        price (float): The price the requester is willing to pay. Must be non-negative.

    Methods:
        upload_request(): Uploads the request details to the database.
        mark_transaction_complete(): Marks the transaction as complete in the database.
    """
    
    def __init__(self, title, description=None, image=None, price=0.0):
        """
        Initializes a new ISORequestor instance with the given parameters.

        Parameters:
            title (str): The title of the item or service being requested.
            description (str, optional): A more detailed description of the item or service.
            image (Image, optional): An image representing the item or service.
            price (float): The price the requester is willing to pay. Cannot be negative.

        Raises:
            ValueError: If the provided price is negative.
        """
    
    def upload_request(self):
        """
        Uploads the request to the database, making it visible to other users
        and recording the details for transaction history.
        """

    def mark_transaction_complete(self):
        """
        Marks the associated transaction as complete in the database. This is used
        to update the transaction history once a successful transaction has been completed.
        """
