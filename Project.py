import re
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging as log

log.basicConfig(filename="logs.txt",filemode="w+",level=log.INFO,format="Level:%(levelname)s Message: \t\t %(message)s")

from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://<user>:<pwd>@cluster0.igje0c8.mongodb.net/?retryWrites=true&w=majority"  #Enter user and pwd here

client = MongoClient(uri)

try:
    client.drop_database('flipkart_scrapper')
except:
    pass


db=client["flipkart_scrapper"]

try:
    client.admin.command('ping')
    log.info("Pinged your deployment. You successfully connected to MongoDB!")
    connection=1
except Exception as e:
    log.error(str(e))
    log.error("Connection failed")
    connection=0
    
links=[]
if(connection!=0):
    try:
        base_url="https://www.flipkart.com/search?q="
        search=input().replace(" ","+")
        full_url=base_url+search
        html_code=bs(((uReq(full_url)).read()),"html.parser")
        l=html_code.findAll("div",{"class":"_2kHMtA"})

        for i in range(len(l)):
            try:
                t="https://www.flipkart.com"+l[i].a["href"]
                if t not in links:
                    links.append(t)
            except:
                pass

        total_val=[i for i in range(len(links))]
        for i in range(len(links)):
            try:
                t=0
                total_val[i]=db[str("Prod. "+str(i+1))]
                code_2=bs(((uReq(links[i])).read()),"html.parser")
                title=code_2.find("span",{"class":"B_NuCI"}).text
                rating=code_2.find("div",{"class":"_3LWZlK"}).text
                total_rating=code_2.find("span",{"class":"_2_R_DZ"}).span.text
                comments=code_2.find("div",{"class":"col JOpGWq"})
                comment_expanded=comments.a["href"]
                comment_expanded=re.sub("aid.*","aid=overall",comment_expanded)
                code_3=bs(uReq("https://www.flipkart.com"+comment_expanded).read(),"html.parser")
                comment_boxes=code_3.findAll("div",{"class":"_1AtVbE col-12-12"})
                try:
                    price=code_2.find("div",{"class":"_30jeq3 _16Jk6d"}).text
                except Exception as e:
                    price=e
                total_val[i].insert_many([{"Name":title,
                                    "Rating":rating,
                                    "Price":price,
                                    "Total Ratings":total_rating}])
                
                values_to_insert=[]
                for j in comment_boxes:
                    dict0={}
                    try:
                        val1=j.div.div.div.p.text
                        try:
                            val2=j.find("div",{"class":""}).text
                            val2=re.sub("READ MORE","",val2)
                            val3=j.find("div",{"class":"_3LWZlK _1BLPMq"}).text
                        except Exception as e:
                            val2=e
                            val3=e
                        dict0[val1]=val2
                        dict0["Rating"]=val3
                        values_to_insert.append(dict0)
                    
                        
                    except Exception as e:
                        val1=e
                        log.error(str(e))
                        pass
                    
                total_val[i].insert_many(values_to_insert)
                        
            except Exception as e:
                log.error(str(e))  

    except Exception as e:
        log.error(str(e))
else:
    pass

log.shutdown()