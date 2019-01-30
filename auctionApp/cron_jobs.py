from django.core.mail import send_mail
from django.db.models.functions import datetime
from django_cron import CronJobBase, Schedule

from auctionApp.models import Auction


class ResolveAuctions(CronJobBase):
    schedule = Schedule(run_every_mins=5) # Resolve auctions every 5 minutes
    code = 'auctionApp.resolve_auctions'

    def do(self):
        print("Resolving auctions...")

        resolvables = []
        for auction in Auction.objects.all():
            if auction.time_closing < datetime.datetime.now() and auction.active and not auction.banned:
                resolvables.append(auction)

        if resolvables is None:
            print('No active unresolved auctions found.')
            return

        for auction in resolvables:
            recipients = [auction.seller_email]
            if auction.bid_set.count() > 0:
                winner_email = auction.bid_set.get(user_id=auction.current_winner_id).email
                recipients.append(winner_email)
                body = 'Auction number %d: "%s" has finished. The highest bid was %d EUR by %s.\n\n' % (auction.id, auction.title, auction.current_price, auction.current_winner_name)
            else:
                body = 'Auction number %d: "%s" has finished. Unfortunately no bids were made.' % (auction.id, auction.title)

            subject = 'Auction "%s" has finished' % auction.title

            send_mail(subject, body, 'resolver@yaas', recipients)

            auction.active = False
            auction.resolved = True
            auction.save()

            print('Auction id %d: "%s" resolved.' % (auction.id, auction.title))

