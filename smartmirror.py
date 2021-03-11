# External Imports
import logging
import queue
from asyncio import shield
from queue import Queue
from tkinter import *
from datetime import datetime
import threading
import time
import aiohttp
import asyncio
import pytz
import coloredlogs
from PIL import Image, ImageTk

# Local Imports
from library.apis import NEWS_API, NewsLocation, WEATHER_API, WeatherLocation

# Logging variables config
logging.captureWarnings(True)
LOGGER = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

# Const Variables
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18
xsmall_text_size = 14
TIME_ZONE = pytz.timezone('Europe/Lisbon')
TIME_FORMAT: str = '%H:%M'
DATE_FORMAT: str = '%d/%m/%Y'

# Icon Mapping
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

# Week Day Mapping -> I do not want to use locale
week_day_lookup = {
    'Monday': "Segunda-Feira",
    'Tuesday': "Terça-Feira",
    'Wednesday': "Quarta-Feira",
    'Thursday': "Quinta-Feira",
    'Friday': "Sexta-Feira",
    'Saturday': "Sábado",
    'Sunday': "Domingo"
}

# Queue with gui update tasks
gui_queue = Queue()


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        """
        Clock Frame located at NW with Hour, day of week and Date
        :param parent:
        :param args:
        :param kwargs:
        """
        Frame.__init__(self, parent, bg='black')
        self.parent = parent
        # initialize time label
        self.current_time = ''
        self.timeLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.current_day = ''
        self.dayLbl = Label(self, text=self.current_day, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.dayLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.current_date = ''
        self.dateLbl = Label(self, text=self.current_date, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        # perform request
        self.get_day_time()

    async def get_day_time(self):
        """
        Get current day, hour and date and send to gui updater queue every second.
        :return:
        """
        while True:
            full_date_time = datetime.now(TIME_ZONE)

            current_day = full_date_time.strftime('%A')
            current_time = full_date_time.strftime(TIME_FORMAT)
            current_date = full_date_time.strftime(DATE_FORMAT)

            # if time string has changed, update it
            if current_time != self.current_time:
                self.current_time = current_time
                gui_queue.put(lambda: ClockGui(self.parent).update_time(current_time, self.timeLbl))
                LOGGER.info("New time/hour sent to GUI queue.")
            if current_date != self.current_date:
                self.current_date = current_date
                gui_queue.put(lambda: ClockGui(self.parent).update_date(current_date, self.dateLbl))
                LOGGER.info("New date sent to GUI queue.")
            if current_day != self.current_day:
                self.current_day = current_day
                gui_queue.put(lambda: ClockGui(self.parent).update_day(current_day, self.dayLbl))
                LOGGER.info("New week day sent to GUI queue.")

            await asyncio.sleep(1)


class ClockGui(Frame):
    def __init__(self, parent):
        """
        Update Gui labels with associated values
        :param parent:
        """
        Frame.__init__(self, parent, bg='black')

    @staticmethod
    def update_time(current_time, time_lbl):
        if current_time:
            time_lbl.config(text=current_time)
            LOGGER.info("GUI updated with new time.")

    @staticmethod
    def update_date(current_date, date_lbl):
        if current_date:
            date_lbl.config(text=current_date)
            LOGGER.info("GUI updated with new date.")

    @staticmethod
    def update_day(current_day, day_lbl):
        if current_day:
            if current_day in week_day_lookup:
                day_lbl.config(text=week_day_lookup[current_day])
            else:
                day_lbl.config(text=current_day)
            LOGGER.info("GUI updated with new week day.")



class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        """
        News Frame located at South with headlines from Portugal and Uk
        :param parent:
        :param args:
        :param kwargs:
        """
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        # initialize titles
        self.title_pt = 'Notícias Portugal'
        self.title_uk = 'News United Kingdom'
        # initialize news from pt label
        self.newsLblPt = Label(self, text=self.title_pt, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLblPt.pack(side=TOP, anchor=W)
        self.newsLblUk = None
        # initialize news from pt container
        self.headlinesContainerPt = Frame(self, bg="black")
        self.headlinesContainerPt.pack(side=TOP, anchor=W)
        # initialize news from uk label
        self.newsLblUk = Label(self, text=self.title_uk, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLblUk.pack(side=TOP, anchor=W)
        # initialize news from uk container
        self.headlinesContainerUk = Frame(self, bg="black")
        self.headlinesContainerUk.pack(side=TOP, anchor=W)
        # perform request
        self.get_headlines()

    async def get_headlines(self):
        """
        Get headlines from pt/uk and send to gui updater queue every 5 minutes.
        :return:
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
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
                        LOGGER.info("Headlines from Portugal sent to GUI queue.")
                        # Add effect of waterfall
                        time.sleep(1)
                    for post in news_uk:
                        gui_queue.put(lambda: NewsGui(self.headlinesContainerUk, post).pack(side=TOP, anchor=W))
                        LOGGER.info("Headlines from Uk sent to GUI queue.")
                        # Add effect of waterfall
                        time.sleep(1)

                    await asyncio.sleep(300)
        except asyncio.TimeoutError:
            LOGGER.critical("Timeout error from headlines, waiting ...")
            await asyncio.sleep(5)
            return await self.get_headlines()



class NewsGui(Frame):
    def __init__(self, parent, event_name=""):
        """
        Update Gui labels with associated headline value and news icon at the beginning
        :param parent:
        :param event_name:
        """
        Frame.__init__(self, parent, bg='black')
        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', xsmall_text_size), fg="white",
                                  bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)
        LOGGER.info("GUI updated with new headline.")


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        """
        Weather Frame located at NE with current weather and forecast from Anadia/Portugal
        :param parent:
        :param args:
        :param kwargs:
        """
        Frame.__init__(self, parent, bg='black')
        self.parent = parent
        # local variables initialization
        self.temperature = None
        self.icon = None
        self.forecast = None
        self.location = None
        self.current_description = None
        self.forecast_info = None
        # Current weather container
        self.currentWeatherContainer = Frame(self, bg="black")
        self.currentWeatherContainer.pack(side=TOP, anchor=W)
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
        # Forecast container
        self.forecastContainer = Frame(self, bg="black")
        self.forecastContainer.pack(side=LEFT, anchor=W)
        # Forecast next day
        self.forecast1Container = Frame(self.forecastContainer, bg="black")
        self.forecast1Container.pack(side=TOP, anchor=W)
        self.forecast1Icon = Label(self.forecast1Container, bg='black')
        self.forecast1Icon.pack(anchor=W)
        self.forecast1Lbl = Label(self.forecast1Container, font=('Helvetica', xsmall_text_size), fg="white", bg="black")
        self.forecast1Lbl.pack(side=LEFT, anchor=W)
        # Forecast next next day
        self.forecast2Container = Frame(self.forecastContainer, bg="black")
        self.forecast2Container.pack(side=TOP, anchor=W)
        self.forecast2Icon = Label(self.forecast2Container, bg='black')
        self.forecast2Icon.pack(anchor=W)
        self.forecast2Lbl = Label(self.forecast2Container, font=('Helvetica', xsmall_text_size), fg="white", bg="black")
        self.forecast2Lbl.pack(side=LEFT, anchor=W)
        # Forecast next next next day
        self.forecast3Container = Frame(self.forecastContainer, bg="black")
        self.forecast3Container.pack(side=TOP, anchor=W)
        self.forecast3Icon = Label(self.forecast3Container, bg='black')
        self.forecast3Icon.pack(anchor=W)
        self.forecast3Lbl = Label(self.forecast3Container, font=('Helvetica', xsmall_text_size), fg="white", bg="black")
        self.forecast3Lbl.pack(side=LEFT, anchor=W)


        self.get_weather()

    async def get_weather(self):
        """
        Get weather from Anadia/PT and send to gui updater queue every 3 minutes.
        Weather object contains forecast information -> weather.forecast
        :return:
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                api = WEATHER_API(session)
                while True:
                    # Location -> Anadia
                    location = WeatherLocation(latitude=40.440811, longitude=-8.435070)

                    # Get weather for my location
                    weather = await location.get(api)

                    if weather is not None:
                        if weather.current_temperature != self.temperature:
                            self.temperature = weather.current_temperature
                            gui_queue.put(lambda: WeatherGui(self.currentWeatherContainer)
                                          .update_temperature(str(weather.current_temperature), self.temperatureLbl))
                            LOGGER.info("Current temperature sent to GUI queue.")
                        if weather.current_main_description != self.icon:
                            self.icon = weather.current_main_description
                            gui_queue.put(lambda: WeatherGui(self.currentWeatherContainer)
                                          .update_icon(weather.current_main_description, self.iconLbl))
                            LOGGER.info("Current icon sent to GUI queue.")
                        if weather.current_description != self.current_description:
                            self.current_description = weather.current_description
                            gui_queue.put(lambda: WeatherGui(self.currentWeatherContainer)
                                          .update_description(weather.current_description, self.currentlyLbl))
                            LOGGER.info("Current weather description sent to GUI queue.")

                        # TODO: Update forecast when ?
                        gui_queue.put(lambda: WeatherGui(self.forecastContainer)
                                      .update_forecast(weather.forecast,
                                                       self.forecast1Lbl,
                                                       self.forecast2Lbl,
                                                       self.forecast3Lbl,
                                                       self.forecast1Icon,
                                                       self.forecast2Icon,
                                                       self.forecast3Icon))

                    await asyncio.sleep(180)
        except asyncio.TimeoutError:
            LOGGER.critical("Timeout error from weather, waiting ...")
            await asyncio.sleep(5)
            return await self.get_weather()


class WeatherGui(Frame):
    def __init__(self, parent, event_name=""):
        """
        Update Gui labels with associated weather values like temperature, description and Icon associated.
        Icons lookup with images located inside /assets folder

        :param parent:
        :param event_name:
        """
        Frame.__init__(self, parent, bg='black')

    @staticmethod
    def update_temperature(current_temperature, temperatureLbl):
        if current_temperature:
            temperatureLbl.config(text=current_temperature + u'\N{DEGREE SIGN}')
            LOGGER.info("GUI updated with new current temperature.")

    @staticmethod
    def update_icon(current_main_description, iconLbl):
        if current_main_description in icon_lookup:
            # Icon lookup key must match the main description
            image = Image.open(icon_lookup[current_main_description])
            image = image.resize((100, 100), Image.ANTIALIAS)
            image = image.convert('RGB')
            photo = ImageTk.PhotoImage(image)

            iconLbl.config(image=photo)
            iconLbl.image = photo
            LOGGER.info("GUI updated with new icon.")


    @staticmethod
    def update_description(current_description, currentlyLbl):
        if current_description:
            currentlyLbl.config(text=current_description.title())
            LOGGER.info("GUI updated with new current weather description.")


    @staticmethod
    def update_forecast(forecast, forecast1Lbl, forecast2Lbl, forecast3Lbl, forecast1Icon, forecast2Icon, forecast3Icon):
        for i in range(1, 4):
            forecast_info = f'- {week_day_lookup[forecast[i].week_day]} - ' \
                            f'{forecast[i].min_temperature}\N{DEGREE SIGN} / ' \
                            f'{forecast[i].max_temperature}\N{DEGREE SIGN}'

            image = Image.open(icon_lookup[forecast[i].short_description])
            image = image.resize((25, 25), Image.ANTIALIAS)
            image = image.convert('RGB')
            photo = ImageTk.PhotoImage(image)

            if i == 1:
                forecast1Lbl.config(text=forecast_info)
                forecast1Icon.config(image=photo)
                forecast1Icon.image = photo
                forecast1Icon.pack(side=LEFT, anchor=W)
            if i == 2:
                forecast2Lbl.config(text=forecast_info)
                forecast2Icon.config(image=photo)
                forecast2Icon.image = photo
                forecast2Icon.pack(side=LEFT, anchor=N)
            if i == 3:
                forecast3Lbl.config(text=forecast_info)
                forecast3Icon.config(image=photo)
                forecast3Icon.image = photo
                forecast3Icon.pack(side=LEFT, anchor=N)


class FullscreenWindow:

    def __init__(self):
        # environment initialization
        self.tk = Tk()
        self.tk.configure(background='black')
        # frame creation
        self.topFrame = Frame(self.tk, background='black')
        self.bottomFrame = Frame(self.tk, background='black')
        self.topFrame.pack(side=TOP, fill=BOTH, expand=YES)
        self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.state = False
        # call to fullscreen feature and close feature
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        # clock
        LOGGER.info("Clock Frame started.")
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)

        # weather
        LOGGER.info("Weather Frame started.")
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)

        # news
        LOGGER.info("News Frame started.")
        self.news = News(self.bottomFrame)
        self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)

        LOGGER.info("Thread with async loop started.")
        threading.Thread(target=self.start_loop).start()

        LOGGER.info("Periodic GUI Updater started.")
        self.periodicGuiUpdate()

    def toggle_fullscreen(self, event=None):
        """
        Call for fulscreen mode
        :param event:
        :return:
        """
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        """
        Exit fullscreen mode
        :param event:
        :return:
        """
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def periodicGuiUpdate(self):
        """
        There's any task inside the gui updater queue? Let's do that!
        :return:
        """
        while True:
            try:
                fn = gui_queue.get_nowait()
                LOGGER.info(f"Task {fn} removed from GUI queue and performed.")
            except queue.Empty:
                break
            fn()
        self.tk.after(100, self.periodicGuiUpdate)

    def start_loop(self):
        """
        Create a new event loop object, create tasks and run them!
        :return:
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.news.get_headlines())
        loop.create_task(self.clock.get_day_time())
        loop.create_task(self.weather.get_weather())
        LOGGER.info("Tasks Created into loop.")
        loop.run_forever()


if __name__ == '__main__':
    LOGGER.critical("This program is distributed in the hope that it will be useful, "
                    "but WITHOUT ANY WARRANTY; without even the implied warranty of "
                    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  "
                    "See the GNU General Public License for more details.")

    w = FullscreenWindow()
    w.tk.mainloop()
