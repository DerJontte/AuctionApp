from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone


class AuctionTestCase(TestCase):

    def setUp(self):
        # Set up three client connections
        c_1 = Client()
        c_2 = Client()
        c_3 = Client()

        # Create three users
        POST_1 = {'username': 'testuser_a',
                  'email': 'test@stuff.com',
                  'password1': 'securepassword',
                  'password2': 'securepassword',
                  'currency': 'SEK'}

        POST_2 = {'username': 'testuser_b',
                  'email': 'test@stuff.com',
                  'password1': 'securepassword',
                  'password2': 'securepassword',
                  'currency': 'SEK'}

        POST_3 = {'username': 'testuser_c',
                  'email': 'test@stuff.com',
                  'password1': 'securepassword',
                  'password2': 'securepassword',
                  'currency': 'EUR'}

        response_3 = c_3.post('/signup/', POST_3)
        self.assertEqual(response_3.status_code, 200)

        response_2 = c_2.post('/signup/', POST_2)
        self.assertEqual(response_2.status_code, 200)

        response_1 = c_1.post('/signup/', POST_1)
        self.assertEqual(response_1.status_code, 200)

    def test_UC3(self):
        # Login testuser A
        c = Client()
        c.login(username='testuser_a', password='securepassword')

        # Let testuser A create an auction with a starting price of 10.00
        POST = {'title': 'Title of test',
                'description': 'This is a very nice test. It can be used again and again. That is why you should have a test like this.',
                'starting_price': 10.00,
                'end_datetime': (timezone.localtime() + timedelta(hours=72)).isoformat()}

        # Post the new auction form and assert that the HTTP response is OK
        response = c.post('/auctions/add/', POST)
        self.assertEqual(response.status_code, 200)

        POST = {'confirmed': 'Yes'}
        response = c.post('/auctions/add/', POST)

        # Assert that the HTTP response is OK and that the info message from the app confirms the auction was added
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Auction added')

    def test_UC6(self):
        # Log in testuser B
        c = Client()
        c.login(username='testuser_b', password='securepassword')

        # Let testuser A create an auction that testuser B can bid on
        self.test_UC3()

        # Bid 11.50 on the auction with a starting price of 10.00
        my_bid = 11.50
        POST = {'action': 'Place bid',
                'new_bid': my_bid}
        response = c.post('/auctions/bid/1', POST)
        context = response.context

        # Assert HTTP response is OK
        self.assertEqual(response.status_code, 200)

        # Confirm the bid
        POST = {'action': 'confirm',
                'bid': context.get('bid')}
        response = c.post('/auctions/bid/1', POST)
        context = response.context

        # Assert HTTP response is OK and that the app confirms bid has been registered without errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'has been registered')
        self.assertIsNone(context.get('error_message'))

        # GET the auction and assert that current price equals the posted bid
        response = c.get('/auctions/1')
        auction = response.context.get('auction')
        self.assertEqual(auction.current_price, my_bid)

        # Send a new preliminary bid. It should not be possible for a user to bid on an auction they are already
        # winning, so the response shall be a 403.
        POST = {'action': 'Place bid',
                'new_bid': my_bid + 1}
        response = c.post('/auctions/bid/1', POST)
        self.assertEqual(response.status_code, 403)

        # Try to 'confirm' a bid that outbids the user's own bid. This should return a 403.
        POST = {'action': 'confirm',
                'bid': my_bid + 2}
        response = c.post('/auctions/bid/1', POST)
        self.assertEqual(response.status_code, 403)

        # Login testuser C
        c.login(username='testuser_c', password='securepassword')

        # Place a bid that is not higher than the current winning bid. The preliminary bid sum in this POST is not
        # checked in the app, so all responses should be OK for now.
        my_bid = 11.50
        POST = {'action': 'Place bid',
                'new_bid': my_bid}
        response = c.post('/auctions/bid/1', POST)
        context = response.context

        # Assert HTTP response is OK
        self.assertEqual(response.status_code, 200)

        # Confirm the bid. Here the app checks that the bid is actually higher than the current winning bid.
        POST = {'action': 'confirm',
                'bid': context.get('bid')}
        response = c.post('/auctions/bid/1', POST)

        # The app should respond that the bid was not registered
        self.assertContains(response, "could not be registered")

