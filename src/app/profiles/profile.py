class UserProfile:
    """
    The UserProfile class allows users to grab a user's contact information and their location for 
    picking up the item they want to buy. It also allows users to view the currently listed items 
    and past items sold. 

    Attributes:
        email (str): The user's email.
        name (str): The user's name.
        profilePicture (Image, optional): A profile picture representing the user.
        location (str): The user's location on campus specifically).
	    phoneNumber (int, optional): The user's phone number (not necessary; can be optional).

    Methods:
        upload_contactInfo(): Uploads the users contact information to the database.
        get_transaction_history(): Provides users with a list of recent transaction history including
	buys, sells, and ISOs.
    """
    
    def __init__(self, email, name, profilePicture=None, location=None, phoneNumber=0):
        """
        Initializes a new User Profile instance with the given parameters.

        Parameters:
            email (str): The user's email.
            name (str): The user's name.
            profilePicture (Image, optional): A profile picture representing the user.
            location (str): The user's location on campus specifically).
	    phoneNumber (int, optional): The user's phone number (not necessary; can be optional).

        Raises:
            ValueError: 
        """
    
    def upload_contactInfo(self):
        """
        Uploads a users contact information, including their name, email, profile picture, optional
	    phone number, to the database, making it visible to buyers.
        """

    def get_transaction_history(self):
        """
        Retrieves a list of a users transaction history and stores it within the database. This is so users can see their
        own transaction and other users transaction history.
        """