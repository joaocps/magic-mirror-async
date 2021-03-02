import queue
from queue import Queue
from tkinter import *
from datetime import datetime
import threading
import time
import aiohttp
import asyncio
import pytz

from PIL import Image, ImageTk

from library.apis import NEWS_API, NewsLocation, WEATHER_API, WeatherLocation

weather_api_token = '<TOKEN>'  # create account at https://darksky.net/dev/
weather_lang = 'en'  # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us'  # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = None  # Set this if IP location lookup does not work for you (must be a string)
longitude = None  # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'Clear': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",  # wind
    'Clouds': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'Rain': "assets/Rain.png",  # rain day
    'Drizzle': "assets/Rain.png",  # rain day
    'Snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'Fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'Tornado': "assests/Tornado.png",  # tornado
    'hail': "assests/Hail.png"  # hail
}

gui_queue = Queue()

TIME_ZONE = pytz.timezone('Europe/Lisbon')
TIME_FORMAT: str = '%H:%M'
DATE_FORMAT: str = '%d/%m/%Y'


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.parent = parent
        # initialize time label
        self.current_time = ''
        self.timeLbl = Label(self, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.current_day = ''
        self.dayLbl = Label(self, text=self.current_day, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dayLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.current_date = ''
        self.dateLbl = Label(self, text=self.current_date, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.get_day_time()

    async def get_day_time(self):
        while True:
            full_date_time = datetime.now(TIME_ZONE)

            current_day = full_date_time.strftime('%A')
            current_time = full_date_time.strftime(TIME_FORMAT)
            current_date = full_date_time.strftime(DATE_FORMAT)

            # if time string has changed, update it
            if current_time != self.current_time:
                self.current_time = current_time
                gui_queue.put(lambda: ClockGui(self.parent).update_time(current_time, self.timeLbl))
            if current_date != self.current_date:
                self.current_date = current_date
                gui_queue.put(lambda: ClockGui(self.parent).update_date(current_date, self.dateLbl))
            if current_day != self.current_day:
                self.current_day = current_day
                gui_queue.put(lambda: ClockGui(self.parent).update_day(current_day, self.dayLbl))

            await asyncio.sleep(1)


class ClockGui(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')

    @staticmethod
    def update_time(current_time, time_lbl):
        if current_time:
            time_lbl.config(text=current_time)

    @staticmethod
    def update_date(current_date, date_lbl):
        if current_date:
            date_lbl.config(text=current_date)

    @staticmethod
    def update_day(current_day, day_lbl):
        if current_day:
            day_lbl.config(text=current_day)


class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title_pt = 'News Portugal'
        self.title_uk = 'News United Kingdom'
        self.newsLblPt = Label(self, text=self.title_pt, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLblPt.pack(side=TOP, anchor=W)
        self.newsLblUk = None
        self.headlinesContainerPt = Frame(self, bg="black")
        self.headlinesContainerPt.pack(side=TOP, anchor=W)
        self.newsLblUk = Label(self, text=self.title_uk, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLblUk.pack(side=TOP, anchor=W)
        self.headlinesContainerUk = Frame(self, bg="black")
        self.headlinesContainerUk.pack(side=TOP, anchor=W)
        self.get_headlines()

    async def get_headlines(self):
        async with aiohttp.ClientSession() as session:
            api = NEWS_API(session)
            while True:
                for widget in self.headlinesContainerPt.winfo_children():
                    widget.destroy()
                for widget in self.headlinesContainerUk.winfo_children():
                    widget.destroy()

                location_pt = NewsLocation("pt")
                location_uk = NewsLocation("uk")

                news_pt = await location_pt.get(api)
                news_uk = await location_uk.get(api)

                for post in news_pt:
                    gui_queue.put(lambda: NewsGui(self.headlinesContainerPt, post).pack(side=TOP, anchor=W))
                    # Add effect of waterfall
                    time.sleep(1)
                for post in news_uk:
                    gui_queue.put(lambda: NewsGui(self.headlinesContainerUk, post).pack(side=TOP, anchor=W))
                    # Add effect of waterfall
                    time.sleep(1)

                await asyncio.sleep(300)


class NewsGui(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')
        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', small_text_size), fg="white",
                                  bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.parent = parent
        self.temperature = None
        self.icon = None
        self.forecast = ''
        self.location = ''
        self.current_description = None
        # Initialize Temperature Frame
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        # Add temperature label
        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        # Add icon to frame
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        # Current description
        self.currentlyLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        # self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.forecastLbl.pack(side=TOP, anchor=W)
        # self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    async def get_weather(self):
        async with aiohttp.ClientSession() as session:
            api = WEATHER_API(session)
            while True:
                # Location -> Anadia
                location = WeatherLocation(latitude=40.440811, longitude=-8.435070)

                # Get weather for my location
                weather = await location.get(api)

                if weather.current_temperature != self.temperature:
                    self.temperature = weather.current_temperature
                    gui_queue.put(lambda: WeatherGui(self.parent)
                                  .update_temperature(str(weather.current_temperature), self.temperatureLbl))
                if weather.current_main_description != self.icon:
                    self.icon = weather.current_main_description
                    gui_queue.put(lambda: WeatherGui(self.parent)
                                  .update_icon(weather.current_main_description, self.iconLbl))
                if weather.current_description != self.current_description:
                    self.current_description = weather.current_description
                    gui_queue.put(lambda: WeatherGui(self.parent)
                                  .update_description(weather.current_description, self.currentlyLbl))

                await asyncio.sleep(30)

    # Dummy method, just for idea caching !
    def get_weathers(self):

        if latitude is None and longitude is None:

            lat = location_obj['latitude']
            lon = location_obj['longitude']

            location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

            # get weather
            weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (
                weather_api_token, lat, lon, weather_lang, weather_unit)
        else:
            location2 = ""
            # get weather
            weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (
                weather_api_token, latitude, longitude, weather_lang, weather_unit)

        r = requests.get(weather_req_url)
        weather_obj = json.loads(r.text)

        degree_sign = u'\N{DEGREE SIGN}'
        temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
        currently2 = weather_obj['currently']['summary']
        forecast2 = weather_obj["hourly"]["summary"]

        icon_id = weather_obj['currently']['icon']
        icon2 = None

        if icon_id in icon_lookup:
            icon2 = icon_lookup[icon_id]

        if icon2 is not None:
            if self.icon != icon2:
                self.icon = icon2
                image = Image.open(icon2)
                image = image.resize((100, 100), Image.ANTIALIAS)
                image = image.convert('RGB')
                photo = ImageTk.PhotoImage(image)

                self.iconLbl.config(image=photo)
                self.iconLbl.image = photo
        else:
            # remove image
            self.iconLbl.config(image='')

        if self.currently != currently2:
            self.currently = currently2
            self.currentlyLbl.config(text=currently2)
        if self.forecast != forecast2:
            self.forecast = forecast2
            self.forecastLbl.config(text=forecast2)
        if self.temperature != temperature2:
            self.temperature = temperature2
            self.temperatureLbl.config(text=temperature2)
        if self.location != location2:
            if location2 == ", ":
                self.location = "Cannot Pinpoint Location"
                self.locationLbl.config(text="Cannot Pinpoint Location")
            else:
                self.location = location2
                self.locationLbl.config(text=location2)

        self.after(600000, self.get_weather)


class WeatherGui(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

    @staticmethod
    def update_temperature(current_temperature, temperatureLbl):
        if current_temperature:
            temperatureLbl.config(text=current_temperature + u'\N{DEGREE SIGN}')

    @staticmethod
    def update_icon(current_main_description, iconLbl):
        if current_main_description in icon_lookup:
            image = Image.open(icon_lookup[current_main_description])
            image = image.resize((100, 100), Image.ANTIALIAS)
            image = image.convert('RGB')
            photo = ImageTk.PhotoImage(image)

            iconLbl.config(image=photo)
            iconLbl.image = photo

    @staticmethod
    def update_description(current_description, currentlyLbl):
        if current_description:
            currentlyLbl.config(text=current_description.title())


class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.calendarLbl = Label(self, text=self.title, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)
        self.get_events()

    def get_events(self):
        # TODO: implement this method
        # reference https://developers.google.com/google-apps/calendar/quickstart/python

        # remove all children
        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        calendar_event = CalendarEvent(self.calendarEventContainer)
        calendar_event.pack(side=TOP, anchor=E)
        pass


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', small_text_size), fg="white",
                                  bg="black")
        self.eventNameLbl.pack(side=TOP, anchor=E)


class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background='black')
        self.bottomFrame = Frame(self.tk, background='black')
        self.topFrame.pack(side=TOP, fill=BOTH, expand=YES)
        self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
        # weather
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
        # news
        self.news = News(self.bottomFrame)
        self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)
        # calender - removing for now
        # self.calender = Calendar(self.bottomFrame)
        # self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)
        threading.Thread(target=self.start_loop).start()
        # Update Gui
        self.periodicGuiUpdate()

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def periodicGuiUpdate(self):
        while True:
            try:
                fn = gui_queue.get_nowait()
            except queue.Empty:
                break
            fn()
        self.tk.after(100, self.periodicGuiUpdate)

    def start_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.news.get_headlines())
        loop.create_task(self.clock.get_day_time())
        loop.create_task(self.weather.get_weather())
        loop.run_forever()


if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()
