#!/bin/env python
import twint  # for scraping twitter
import snscrape.modules.reddit as snreddit # for scraping reddit
from pymongo.mongo_client import MongoClient # for storage
from tkinter import * # for GUI



# Scraping
# -------------------------------------------------------
def scrapeTwitter(query, amount):
    tweets = []
    c = twint.Config()
    c.Search = query
    c.Limit = amount
    c.Lang = "en"
    c.Store_object = True
    c.Store_object_tweets_list = tweets
    c.Hide_output = True
    twint.run.Search(c)
    return [{ 
               "date": tweet.datestamp
              ,"time": tweet.timestamp
              ,"text": tweet.tweet
            } for tweet in tweets ]


def scrapeReddit(subreddit, amount):
    posts = []
    for i,post in enumerate(snreddit.RedditSubredditScraper(subreddit).get_items()):
        if i>amount: 
            break
        if isinstance(post, snreddit.Comment):
            posts.append({"datetime": post.created, "text": post.body})
        elif isinstance(post, snreddit.Submission):
            posts.append({"datetime": post.created, "text": post.selftext})
    return posts


# Storage
# -------------------------------------------------------
def toMongo(host,port,database_name,collection_name,items):
    client = MongoClient(host, port)
    database = client[database_name]
    collection = database[collection_name]
    for item in items:
        collection.insert_one(item)


# GUI
# -------------------------------------------------------

def GUI():
    default_text  = "Wating for action"
    scraping_text = "Scraping..."
    done_text     = "DONE"
    twitter_scraper_str = "twint (for twitter)"
    reddit_scraper_str = "snscrape (for reddit)"

    root = Tk()
    # mongdb config 
    ###############################
    Label(root, text='MongoDB config'). grid(row=0)
    Label(root, text='host').           grid(row=1)
    Label(root, text='port').           grid(row=2)
    Label(root, text='database name').  grid(row=3)
    Label(root, text='collection name').grid(row=4)
    input_host = Entry(root)
    input_port = Entry(root)
    input_database_name  = Entry(root)
    input_collection_name = Entry(root)
    input_host           .grid(row=1, column=1)
    input_port           .grid(row=2, column=1)
    input_database_name  .grid(row=3, column=1)
    input_collection_name .grid(row=4, column=1)

    # twitter scrape options
    ###############################
    label_twitter_query  = Label(root, text="Query")
    label_twitter_amount = Label(root, text="amount")
    label_twitter_query.grid(row=6)
    label_twitter_amount.grid(row=7)
    twitter_input_query = Entry(root)
    twitter_input_amount = Entry(root)
    twitter_input_query.grid(row=6, column=1)
    twitter_input_amount.grid(row=7, column=1)
    label_twitter_query  .grid_remove()
    label_twitter_amount .grid_remove()
    twitter_input_query  .grid_remove()
    twitter_input_amount .grid_remove()

    # reddit scrape options
    ###############################
    label_reddit_query  = Label(root, text="subreddit")
    label_reddit_amount = Label(root, text="amount")
    label_reddit_query.grid(row=6)
    label_reddit_amount.grid(row=7)
    reddit_input_query = Entry(root)
    reddit_input_amount = Entry(root)
    reddit_input_query.grid(row=6, column=1)
    reddit_input_amount.grid(row=7, column=1)
    label_reddit_query  .grid_remove()
    label_reddit_amount .grid_remove()
    reddit_input_query  .grid_remove()
    reddit_input_amount .grid_remove()
    
    # Scraper selector:
    ###############################
    def selectScraper(choise):
        if choise == twitter_scraper_str:
            label_reddit_query  .grid_remove()
            label_reddit_amount .grid_remove()
            reddit_input_query  .grid_remove()
            reddit_input_amount .grid_remove()
            label_twitter_query   .grid()
            label_twitter_amount  .grid()
            twitter_input_query   .grid()
            twitter_input_amount  .grid()
            btn.grid()
            massagelabel.grid()
        elif choise == reddit_scraper_str:
            label_twitter_query  .grid_remove()
            label_twitter_amount .grid_remove()
            twitter_input_query  .grid_remove()
            twitter_input_amount .grid_remove()
            label_reddit_query   .grid()
            label_reddit_amount  .grid()
            reddit_input_query   .grid()
            reddit_input_amount  .grid()
            btn.grid()
            massagelabel.grid()

    Label(root, text='select scraper').grid(row=5)
    selectedScraped = StringVar(root)
    w = OptionMenu(root, selectedScraped, twitter_scraper_str, reddit_scraper_str ,command=selectScraper)
    w.grid(row=5, column=1)

    
    massagelabel = Label(root, text=default_text)
    massagelabel.grid(row=9, column=1)
    massagelabel.grid_remove()

    def check_args_not_empty(*args):
        for arg in args:
            if arg == "" or arg == None:
                raise Exception("missing arguments")
    
    def clicked():
        allgood = True
        massagelabel.configure(text=scraping_text)
        try:
            scraper = lambda a,b:[]
            query,amount =None,None
            host = input_host.get()
            port = int(input_port.get())
            database_name = input_database_name.get()
            collection_name = input_collection_name.get()
            if selectedScraped.get() == twitter_scraper_str:
                query  = twitter_input_query.get()
                amount = int(twitter_input_amount.get())
                scraper = scrapeTwitter
            elif selectedScraped.get() == reddit_scraper_str:
                query  = reddit_input_query.get()
                amount = int(reddit_input_amount.get())
                scraper = scrapeReddit
            check_args_not_empty(host,port,database_name,collection_name,query,amount)
            toMongo(host,int(port),database_name,collection_name, scraper(query, int(amount)))

        except ValueError:
            massagelabel.configure(text=("port and amount should be integers"))
            allgood = False
           
        except Exception as e:
            massagelabel.configure(text=str(e))
            allgood = False
        if allgood:
            massagelabel.configure(text=done_text)
    
    btn = Button(root, text="Start", command=clicked)
    btn.grid(row=8, column=0)   
    btn.grid_remove()           
    
    mainloop()


if __name__ == "__main__":
    GUI()
