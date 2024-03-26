class UserProfile:
    """
    The UserProfile class allows users to manage their profile information, view transaction history,
    and interact with the platform. It also provides a user's location to pick up the item they want to buy. 

    Attributes:
        email (str): The user's email.
        name (str): The user's name.
        profile_picture (Image, optional): A profile picture representing the user.
        location (str): The user's location on campus specifically).
        phone_number (int, optional): The user's phone number (not necessary; can be optional).

    Methods:
        upload_contact_info(): Uploads the users contact information to the database.
        get_list_of_items(): Provides a list of items associated with a given user.
        get_transaction_history(): Provides users with a list of recent transaction history including
        buys, sells, and ISOs.
    """
    
    def __init__(self, email, name, profile_picture=None, location=None, phone_number=0):
        """
        Initializes a new User Profile instance with the given parameters.

        Parameters:
            email (str): The user's email.
            name (str): The user's name.
            profile_picture (Image, optional): A profile picture representing the user.
            location (str): The user's location on campus specifically).
            phone_number (int, optional): The user's phone number (not necessary; can be optional).

        Raises:
            ValueError: If the provided phone number is negative.
        """
    
    def upload_contact_info(self):
        """
        Uploads a users contact information, including their name, email, profile picture, optional
        phone number, to the user database, making it visible to buyers.
        """

    def get_list_of_items(self, user_id):
        """
        Retrieves a list of items associated with a given user from the itemsForSale and itemsForRent 
        database and stores it within the user database, making it visible to buyers. 
        This allows potential buyers to view items listed by the user.

        Parameters:
            user_id (int): The unique identifier of the user whose items are to be retrieved.
        
        Returns:
            list: A list of items associated with the specified user.
        """

    def get_transaction_history(self, user_id):
        """
        Retrieves a list of the user's transaction history and stores it within the user database. This includes 
        recent transactions such as buys, sells, and ISOs. Users can use this method to review their own 
        transaction history and other users' transaction history.
        
        Parameters:
        user_id (int): The unique identifier of the user whose transaction history is to be retrieved.
        
        Returns:
            list: A list of the user's transaction history, including buys, sells, and ISOs.
        """