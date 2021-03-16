# Asyncio Smart Mirror - Complete Guide - Hardware & Software

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/joaocps/magic-mirror-async/commits/main) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=joaocps_magic-mirror-async&metric=alert_status)](https://sonarcloud.io/dashboard?id=joaocps_magic-mirror-async) ![Made with](https://img.shields.io/badge/Made%20with-Python-blue)
 
 ![Final Result](/pictures/final_result.jpg)
 
Hello everyone! :wave:

In this repository you will find all the information you need to build your own smart mirror. First of all I want to let you know that this is the cheapest possible implementation, I also leave the prices of most things so you can have some idea when buying your material. In the next sections I present the project a little better and then the focus will be on the crucial parts of the development, whether it is hardware or software.

If you like the work I did and helped you in some way don't forget to click on the button below and pay me a coffee (or a beer, I prefer :smile:).
 
 <a href="https://www.buymeacoffee.com/joaocps" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

## Table of contents
* [Software](#software)
    * [Stack](#stack)
    * [Features](#features)
    * [Setup](#setup)
* [Hardware](#hardware)
    * [Stack](#stack)
    * [Setup](#setup)
* [Credits](#credits)

## General Info (TL;DR)

Smart-Mirror totally “Do It Yourself” with async requests to different api’s. The main objective would be to do all the work without resorting to existing software and build the structure for the mirror 100% by myself. I used asynchronous requests to obtain data from different apis like google news and weather to be able to present and update information from Portugal and UK.

Time-Lapse -> https://www.youtube.com/watch?v=CmpsJ-a0FWg

## Software

 ![Software Image](/pictures/software.png)

### Stack

Software | Version
------------ | -------------
python3 | >= 3.6
python3-tk | 8.6.x
aiohttp | 3.7.4
asyncio | 3.4.3
requests | 2.25.1
feedparser | 6.0.2
pillow | 8.1.1
coloredlogs | 15.0

### Features

- Current Hour, Date and WeekDay.
- Current Weather, Description and related Icon.
- Forecast for 3 days, with min/max temperature and associated icon.
- Main news from Portugal and United Kingdom.

![Diagram](/pictures/feature_diagram.png)

The asyncio package is billed by the Python documentation as a library to write concurrent code. However, async IO is not threading, nor is it multiprocessing. It is not built on top of either of these. It has been said in other words that async IO gives a feeling of concurrency despite using a single thread in a single process. Coroutines (a central feature of async IO) can be scheduled concurrently, but they are not inherently concurrent.

- Asynchronous routines are able to “pause” while waiting on their ultimate result and let other routines run in the meantime.
- Asynchronous code, through the mechanism above, facilitates concurrent execution. To put it differently, asynchronous code gives the look and feel of concurrency.


Most likely you have already watched the television series: The Queen's Gambit. In one of the episodes the main character plays chess against several players at the same time. We can look at this in a synchronous or asynchronous way and more easily perceive the differences between the two. :wink:

**Assumptions:**

- 24 opponents
- Judit makes each chess move in 5 seconds
- Opponents each take 55 seconds to make a move
- Games average 30 pair-moves (60 moves total)

**Synchronous version:** Judit plays one game at a time, never two at the same time, until the game is complete. Each game takes (55 + 5) * 30 == 1800 seconds, or 30 minutes. The entire exhibition takes 24 * 30 == 720 minutes, or 12 hours.

**Asynchronous version:** Judit moves from table to table, making one move at each table. She leaves the table and lets the opponent make their next move during the wait time. One move on all 24 games takes Judit 24 * 5 == 120 seconds, or 2 minutes. The entire exhibition is now cut down to 120 * 30 == 3600 seconds, or just 1 hour.

There is only one Judit, who has only two hands and makes only one move at a time by herself. But playing asynchronously cuts the exhibition time down from 12 hours to one. So, cooperative multitasking is a fancy way of saying that a program’s event loop (more on that later) communicates with multiple tasks to let each take turns running at the optimal time. Async IO takes long waiting periods in which functions would otherwise be blocking and allows other functions to run during that downtime.

TL:DR | 
------------ | 
In this case it was necessary to abstract the gui from the internal ordering processes. This way, a queue is created that receives update instructions for the gui whenever they are different from the current displayed value. The event loop contains the various tasks with different waiting times due to their greater need for updating. When the task is performed, the values are compared with the current values of the gui, if they are different they jump to the queue and are updated.

### Setup

## Hardware

### Stack
Hardware | Price
------------ | -------------
Content from cell 1 | Content from cell 2
Content in the first column | Content in the second column

## Credits

@HackerShackOfficial
