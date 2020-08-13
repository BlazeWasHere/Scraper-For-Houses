from re import compile, findall
from datetime import date
from requests import get
import sqlite3

#   Blaze 
#   Is
#   Sexy
#   IKR


regex = compile(r'<span class="search-result-info center-block">(.*)<')
URL = 'https://www.immoscoop.be/eng/immo_mobile.php?city_or_postcode=Antwerpen+%2B+Deelgemeenten&category=&min_price=0&max_price=&bedroom=&baths=&order=date&proptype=Sale'

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"
}


class Scrape:
    """Scrapes the site and parses the address, bed, plot & living size"""
    def __init__(self):
        self.x = False
        self.req = get(URL,headers=headers).text
        #self.req = codecs.open("ok.html").read()
        # starting
        self.parse()


    def stop_dupe(self):
        connection = sqlite3.connect("houses.db")
        cursor = connection.cursor()
        query = f"""
                SELECT * FROM houses
                WHERE address = '{self.address}'
                """
        for row in cursor.execute(query):
            connection.commit() 
            print(row[0])
            print('ok')
            dupe = True #dupe found
            break
        else:
            dupe = False #no dupe found
            print('nop')
        return dupe


    def parse_address(self):
        self.address = self.cleaned.replace('<br/> ','')
        print(self.address)
        dupe = self.stop_dupe()
        print(dupe)
        if not dupe:
            self.address_write()
        # switch gate on
        self.x =  True

    def address_write(self):
        connection = sqlite3.connect("houses.db")
        cursor = connection.cursor()
        time = date.today()
        query = f"""
                INSERT INTO houses 
                ( date, address ) 
                VALUES 
                ( '{time}', '{self.address}' )
                """
        cursor.execute(query)
        connection.commit()
        #print("Record inserted successfully ", cursor.rowcount)
        cursor.close()


    def parse_bed(self):
        # Beds: 2</span>... => 2</span>...
        self.bed = self.cleaned.split(' ')[1]
        # 2</span>... => 2
        self.bed = self.bed.split('</span>')[0]
        print(self.bed)
        self.bed_write()
        # calling other functions due to them using same line
        self.parse_url()
        self.parse_living()
        self.parse_plot()
        # switch gate off
        self.x = False

    def bed_write(self):
        connection = sqlite3.connect("houses.db")
        cursor = connection.cursor()
        query = f"""
                UPDATE houses 
                SET beds = {self.bed}
                WHERE address = '{self.address}'
                """
        cursor.execute(query)
        connection.commit()
        #print("Record inserted successfully ", cursor.rowcount)
        cursor.close()


    def parse_url(self):
        #  wrapper-top"><a href="https... => https...
        #print(self.cleaned)
        self.url = self.cleaned.split('<a href="')[1]
        # https://www.immoprimo..." => https://www.immoprimo...
        self.url = self.url.split('"')[0]
        print(self.url)
        self.url_write()

    def url_write(self):
        connection = sqlite3.connect("houses.db")
        cursor = connection.cursor()
        query = f"""
                UPDATE houses 
                SET url = '{self.url}'
                WHERE address = '{self.address}'
                """
        cursor.execute(query)
        connection.commit()
        #print("Record inserted successfully ", cursor.rowcount)
        cursor.close()


    def parse_living(self):
        try:
            # center-block">Living Area: 189 m<sup> => 189 m<sup>
            self.living = self.cleaned.split('Living Area: ')[1]
            # 189 m<sup> => 189
            self.living = self.living.split(' ')[0]
        except IndexError:
            # if living not found (cant be parsed)
            self.living = False
        print(self.living)
        if self.living:
            self.living_write()
    
    def living_write(self):
        connection = sqlite3.connect("houses.db")
        cursor = connection.cursor()
        query = f"""
                UPDATE houses 
                SET living = {self.living}
                WHERE address = '{self.address}'
                """
        cursor.execute(query)
        connection.commit()
        #print("Record inserted successfully ", cursor.rowcount)
        cursor.close()


    def parse_plot(self):
        try:
            # center-block">Plot Area: 174 m<sup> => 174 m<sup>2
            self.plot = self.cleaned.split('Plot Area: ')[1]
            # 174 m<sup>2 => 174
            self.plot = self.plot.split(' ')[0]
        except IndexError:
            self.plot = False
        print(self.plot)
        if self.plot:
            self.plot_write()

    def plot_write(self):
        connection = sqlite3.connect("houses.db")
        cursor = connection.cursor()
        query = f"""
                UPDATE houses 
                SET plot = {self.plot}
                WHERE address = '{self.address}'
                """
        cursor.execute(query)
        connection.commit()
        #print("Record inserted successfully ", cursor.rowcount)
        cursor.close()


    def parse(self):
        text = findall(regex, self.req, flags=0)
        #place = regex.search(req).group(1).replace(" <br/>","")
        for house in text:
            self.cleaned = house.replace('\t','')
            #print(self.cleaned)
            if not self.x:
                self.parse_address()   
            elif self.x:
                self.parse_bed()


if __name__ == '__main__':
    Scrape()
        

