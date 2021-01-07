import asyncio
import datetime
import os
import pickle

from googleapiclient.discovery import build
import dateutil.parser
import discord
import html2text as html2text
from pytz import timezone
from discord.ext import tasks, commands

from core.utils import codeblock

TIMEZONE = timezone('Europe/Berlin')


class Calendar(commands.Cog):
    refresh_interval = 15

    def __init__(self, eit):
        self.eit = eit
        self.messagespath = self.eit.bot.datapath/'calendarmessages.pickle'
        self.reminders = []

        self.channels = {'admin': self.eit.admin_calendar}
        for semester in self.eit.semester:
            self.channels.update({semester.name: semester.announcement_channel})

        asyncio.create_task(self.delete_messages())

        self.refresh.start()

    @tasks.loop(seconds=refresh_interval)
    async def refresh(self):
        # Fetch the next 5 entries per calendar
        loop = asyncio.get_running_loop()
        events = await loop.run_in_executor(None, fetch_entries)

        # Check all current reminders for updates
        for reminder in self.reminders:
            for event in events:
                if reminder.id == event['id']:
                    event_updated = dateutil.parser.parse(event['updated']).astimezone(TIMEZONE)
                    if event_updated != reminder.updated:
                        reminder.update_reminder(event)
                    events.remove(event)
                    break
            else:
                reminder.delete_reminder()

        # Got new events
        for event in events:
            channel = self.eit.admin_calendar
            for semester in self.eit.semester:
                if semester.name.lower() in event["organizer"]["displayName"].lower():
                    channel = semester.announcement_channel

                for study_group in semester.study_groups:
                    if study_group.lower() in event["organizer"]["displayName"].lower():
                        channel = semester.announcement_channel
                        break

            self.reminders.append(Reminder(self, event, channel))

    async def delete_messages(self):
        for channel in self.channels.values():
            await channel.purge()

    @commands.command()
    async def ongoing(self, context):
        """Zeigt alle laufenden Termine an"""
        output = ''
        if not self.reminders:
            await context.channel.send('Es gibt momentan keine laufenden Termine!')
        else:
            for reminder in self.reminders:
                if reminder.is_running:
                    output += f'{reminder.calendar_name}: {reminder.summary}\n'
            await context.channel.send(codeblock(output))


class Reminder:
    def __init__(self, calendar_object, event, channel):
        self.calendar_object = calendar_object

        self.id = event['id']
        self.updated = dateutil.parser.parse(event['updated']).astimezone(TIMEZONE)
        self.is_running = False

        self.channel = channel
        self.message = None
        self.embed = None

        # event attributes
        self.calendar_name = None
        self.summary = None
        self.event_start = None
        self.event_end = None
        self.event_duration = None
        self.reminder_start = None
        self.description = None
        self.location = None
        self.colour = None

        self.parse_event(event)
        self.generate_embed()

        self.task = asyncio.create_task(self.refresh())

    async def refresh(self, refresh_interval=20):
        while True:
            try:
                now = datetime.datetime.now(TIMEZONE)
                if self.event_end <= now:
                    self.delete_reminder()
                elif self.reminder_start <= now:
                    self.set_embed_title()
                    if self.message:
                        await self.update_message()
                    else:
                        self.is_running = True
                        self.message = await self.channel.send(embed=self.embed)
                elif self.message:
                    await self.delete_message()

                await asyncio.sleep(refresh_interval)

            except asyncio.CancelledError:
                pass

    async def delete_message(self):
        try:
            await self.message.delete_reminder()
        except AttributeError:
            pass
        except discord.NotFound:
            pass

    async def update_message(self):
        try:
            await self.message.edit(embed=self.embed)
        except discord.NotFound:
            pass

    def delete_reminder(self):
        self.task.cancel()
        asyncio.create_task(self.delete_message())
        try:
            self.calendar_object.reminders.remove(self)
        except ValueError:
            pass

    def update_reminder(self, event):
        self.parse_event(event)
        self.generate_embed()
        if self.message:
            self.set_embed_title()
            asyncio.create_task(self.message.edit(embed=self.embed))

    def parse_event(self, event):
        self.updated = dateutil.parser.parse(event['updated']).astimezone(TIMEZONE)

        # mandatory
        self.calendar_name = event["organizer"]["displayName"]
        self.summary = event["summary"]
        self.event_start = parse_time(event, 'start')

        # optional
        if 'end' in event:
            self.event_end = parse_time(event, 'end')
            self.event_duration = self.event_end - self.event_start
        else:
            self.event_end = None
            self.event_duration = None

        if 'reminders' in event and 'overrides' in event['reminders']:
            remind_minutes = event['reminders']['overrides'][0]['minutes']
        else:
            remind_minutes = 30
        self.reminder_start = self.event_start - datetime.timedelta(minutes=remind_minutes)

        if 'description' in event:
            self.description = html2text.html2text(event['description'])
        else:
            self.description = ''

        if 'location' in event:
            self.location = event['location']
        else:
            self.location = None

        if 'calendarColorId' in event:
            self.colour = discord.Colour(int(event['calendarColorId'].lstrip('#'), 16))
        else:
            self.colour = discord.Colour(0x000000)

    def generate_embed(self):
        embed = discord.Embed(description=self.description, colour=self.colour)

        if self.location:
            embed.add_field(name="Ort / URL", value=self.location, inline=False)

        embed.add_field(name="Datum", value=self.event_start.strftime("%d.%m.%Y"), inline=False)
        embed.add_field(name="Beginn", value=self.event_start.strftime("%H:%M"), inline=True)

        if self.event_duration and self.event_end:
            embed.add_field(name="Dauer", value=(str(self.event_duration)[:-3]), inline=True)
            embed.add_field(name="Ende", value=self.event_end.strftime("%H:%M"), inline=True)

        self.embed = embed

    def set_embed_title(self):
        seconds_until_event = (self.event_start - datetime.datetime.now(TIMEZONE)).total_seconds()
        self.embed.title = f'**{self.calendar_name}**:  {self.summary} {format_seconds(seconds_until_event)}'


def fetch_entries(limit=5, max_seconds_until_remind=300):
    """ Fetches upcoming calendar entries

    Parameters
    ----------
    limit:  The maximum amount of calendar entries fetched per calendar

    Returns
    -------
    A flattened list of calendar entries
    """

    creds = None

    if os.path.exists('data/google/token.pickle'):
        with open('data/google/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    service = build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    calendars_result = service.calendarList().list().execute()
    events = []

    current_time = datetime.datetime.now(TIMEZONE)

    for calendar_info in calendars_result['items']:
        calendar = service.events().list(calendarId=calendar_info['id'], timeMin=now,
                                         maxResults=limit,
                                         singleEvents=True,
                                         orderBy='startTime').execute()

        for entry in calendar['items']:
            if 'backgroundColor' in calendar_info:
                entry['calendarColorId'] = calendar_info['backgroundColor']

            if (parse_remind_time(entry) - current_time).total_seconds() <= max_seconds_until_remind:
                events.append(entry)

    return events


def parse_time(event, event_time_key):
    """Helper function that gets the in :event_time_key: specified time string
    from the entry dict and returns it as an datetime object"""

    if 'dateTime' in event[event_time_key]:
        time_unparsed = event[event_time_key]['dateTime']
        return dateutil.parser.parse(time_unparsed).astimezone(TIMEZONE)
    elif 'date' in event[event_time_key]:
        time_unparsed = event[event_time_key]['date']
        return dateutil.parser.parse(time_unparsed).astimezone(TIMEZONE)
    else:
        print("No date or dateTime key in entry dict recieved from Google Calendar API. Ignoring entry.")


def format_seconds(seconds):
    dayflag = False
    hourflag = False

    if seconds > 0:
        output = 'in '
    else:
        seconds *= -1
        output = 'seit '

    # Tage
    days = int(seconds / 86400)
    if days >= 1:
        dayflag = True
        if days < 2:
            output += 'einem Tag'
        else:
            output += f'{days} Tagen'
        seconds -= days*86400

    # Stunden
    hours = int(seconds / 3600)
    if hours >= 1:
        hourflag = True
        if dayflag:
            output += ' und '
        else:
            output += ', '

        if hours < 2:
            output += 'einer Stunde'
        else:
            output += f'{hours} Stunden'
        seconds -= hours*3600
    elif dayflag:
        output += '.'
        return output

    if dayflag:
        output += '.'
        return output
    elif hourflag:
        output += ' und '

    # Minuten
    minutes = int(seconds / 60)
    if minutes >= 2:
        output += f'{minutes} Minuten.'
    elif minutes >= 1:
        output += 'einer Minute.'
    else:
        output += 'weniger als einer Minute.'

    return output


def parse_remind_time(event):
    if 'reminders' in event and 'overrides' in event['reminders']:
        remind_minutes = event['reminders']['overrides'][0]['minutes']
    else:
        remind_minutes = 30
    return parse_time(event, 'start') - datetime.timedelta(minutes=remind_minutes)
