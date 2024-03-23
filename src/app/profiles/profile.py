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
	    phone number, to the database, making it visible to buyers.
        """

    def get_list_of_items(self):
        """
        Retrieves a list of items associated with a given user stores it within the database, 
        making it visible to buyers.
        """

    def get_transaction_history(self):
        """
        Retrieves a list of a users transaction history and stores it within the database. This is so users can see their
        own transaction and other users transaction history.
        """