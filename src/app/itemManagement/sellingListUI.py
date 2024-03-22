class SellingListingUI:
    """
    The SellingListingUI class allows users to list items or services for sale or rent 
    on the application. It provides the functionality to input details about the item 
    or service, including categorization, pricing, and availability for rentable items.

    Attributes:
        title (str): The title of the item or service being sold or rented.
        description (str, optional): A detailed description of the item or service.
        category (str): The category under which the item or service falls.
        price (float): The asking price for the item or service. Must be non-negative.
        image (Image, optional): An image representing the item or service.
        availability_dates (tuple, optional): A tuple containing start and end dates for the availability of a rentable item.

    Methods:
        upload_listing(): Uploads the item or service details to the database, making it available in the marketplace.
        update_listing_status(listing_id, status): Updates the status of an existing listing.
        set_transaction_timestamp(listing_id): Records the time when a transaction related to the listing is completed.
    """

    def __init__(self, title, category, price, description=None, image=None, availability_dates=None):
        """
        Initializes a new instance of SellingListingUI with the given item or service details.

        Parameters:
            title (str): The title of the item or service being listed.
            category (str): The category of the item or service.
            price (float): The price of the item or service. Cannot be negative.
            description (str, optional): A detailed description of the item or service.
            image (Image, optional): An image representing the item or service.
            availability_dates (tuple, optional): Start and end dates for rentable item availability.

        Raises:
            ValueError: If the provided price is negative.
        """

    def upload_listing(self):
        """
        Uploads the listing to the database. This includes all attributes of the listing, 
        making it visible to other users in the marketplace.
        """

    def update_listing_status(self, listing_id, status):
        """
        Updates the status of a specific listing, identified by listing_id, in the database. 
        This could be used to mark an item as sold, rented, or available again.

        Parameters:
            listing_id (str): The unique identifier of the listing to update.
            status (str): The new status of the listing (e.g., 'available', 'sold', 'rented').
        """

    def set_transaction_timestamp(self, listing_id):
        """
        Records the timestamp when a transaction related to the listing is completed. 
        This is used for updating the transaction history.

        Parameters:
            listing_id (str): The unique identifier of the listing for which the transaction is completed.
        """
