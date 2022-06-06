import asyncio
import feedparser
from pyrogram import Client
from GenericFeed.config import (
        BOT_TOKEN, API_ID,
        API_HASH, FEED_FORMATTER_TEMPLATE
)
from GenericFeed.feed import Feed
from GenericFeed.chat import Chat


async def StartFeedLoop(bot: Client):
    feed = Feed()
    while True:
        feed_items = feed.get_feeds()  # Get feeds from the DB
        for item in feed_items:
            print('-+-' * 20)
            feed_url = item['url']
            print(f'[+] Feed URL: {feed_url}')
            have_update = feed.check_update(feed_url)  # Check if there is an update
            print(f'[+] Have update: {have_update}')
            if have_update:
                feed.update_feed(feed_url)  # Update the feeds
                feed_item = feedparser.parse(feed_url)  # Parse the feed
                for chat in Chat().get_chats():
                    print(
                        f'[+] Sending to chat: {chat["chat_name"]} | {chat["chat_id"]}'
                    )
                    try:
                        await bot.send_message(
                            chat_id=chat['chat_id'],
                            text=FEED_FORMATTER_TEMPLATE.format(
                                feed_title=feed_item['feed']['title'],
                                title=feed_item.entries[0].title,
                                url=feed_item.entries[0].link,
                                summary=feed_item.entries[0].summary,
                            )
                        )
                    except Exception as e:
                        print(f'[!] Error sending message to {chat["chat_name"]} | {chat["chat_id"]}')
                        print(f'[!] Error: {e}')
                        print('[!] Removing chat from DB')
                        Chat().remove_chat(chat['chat_id'])
        await asyncio.sleep(60)


class GenericFeed(Client):
    def __init__(self):
        super().__init__(
            "GenericFeed",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=4,
            plugins=dict(
                root="GenericFeed/plugins"
            ),
        )

    async def start(self):
        await super().start()
        await StartFeedLoop(self)
