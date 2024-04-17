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

######################

#!/usr/bin/python3

from typing import Optional
from database import DatabaseConnection  # Example placeholder for database connection module
from image_processor import ImageProcessor  # Example placeholder for image processing module

class UserProfile:
    """
    The UserProfile class allows users to manage their profile information, view transaction history,
    and interact with the platform. Additionally, it provides functionality for users to specify their
    location for picking up items they want to buy.

    Attributes:
        email (str): The user's email.
        name (str): The user's name.
        profile_picture (Image, optional): A profile picture representing the user.
        location (str): The user's location on campus specifically).
	    phone_number (int, optional): The user's phone number (not necessary; can be optional).
        database (DatabaseConnection): Connection to the application's database for record operations.
        image_processor (ImageProcessor): Processor for handling and storing request images.
    
    Methods:
        __init__(self, title, description, image, price): Initializes a new User Profile instance.
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
        This method retrieves the list of items associated with the user specified by the provided 
        user_id from the user database and returns it for further processing or display to potential buyers.

        Parameters:
            user_id (int): The unique identifier of the user whose items are to be retrieved.
        
        Returns:
            list: A list of items associated with the specified user.
        """

    def get_transaction_history(self, user_id):
        """
        This method fetches the transaction history of the user identified by the provided user_id from 
        the database, including recent transactions such as purchases, sales, and ISOs (In Search Of), 
        allowing users to review their own transaction history and the transaction history of other users.

        Parameters:
        user_id (int): The unique identifier of the user whose transaction history is to be retrieved.
        
        Returns:
            list: A list of the user's transaction history, including buys, sells, and ISOs.
        """