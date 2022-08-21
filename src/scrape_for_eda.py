from scrape_and_save_gui import scrapeReddit,scrapeTwitter,toMongo

if __name__ == "__main__":
    toMongo("localhost",27017,"test", "twitterdb",scrapeTwitter("#happy", 10000))
    toMongo("localhost",27017,"test", "redditdb",scrapeReddit("happy", 10000))

