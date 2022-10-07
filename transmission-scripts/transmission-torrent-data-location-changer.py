#!/usr/bin/python3

# A script to interactively change the data location for Transmission torrents
# Copyright (C) 2022 Louis Lacoste

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import transmission_rpc
import os
import pathlib
import yaml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


# Reading from config
with open(SCRIPT_DIR + "/config.yml", 'r', encoding="utf8") as ymlconfig:
    config = yaml.load(ymlconfig, Loader=yaml.Loader)

if not config:
    raise ValueError("Something went wrong while loading config.")

verbose = config['verbose']

transmissionProtocol = config['transmission']['protocol']
transmissionHost = config['transmission']['host']
transmissionPort = config['transmission']['port']

# Establishing connection to the Transmission instance
# with the parameters provided in config
if verbose:
    print(
        f"Connecting to transmission at {transmissionHost}:{transmissionPort}")
if config['transmission']['auth']['auth_enabled']:
    if verbose:
        print("Authentication enabled ! Using the credentials to connect")
    transmissionUsername = config['transmission']['auth']['username']
    transmissionPassword = config['transmission']['auth']['password']

    transmissionClient = transmission_rpc.client.Client(
        protocol=transmissionProtocol, username=transmissionUsername, password=transmissionPassword,
        host=transmissionHost, port=transmissionPort)
else:
    transmissionClient = transmission_rpc.client.Client(
        protocol=transmissionPort, host=transmissionHost, port=transmissionPort)

incompleteTorrentsList = [
    torrent for torrent in transmissionClient.get_torrents() if torrent.available != 100.0]

# for incompleteTorrent in incompleteTorrentsList:
#     print("------")
#     print(
#         f"Torrent name: {incompleteTorrent.name}\nTorrent data location: {incompleteTorrent.download_dir}")
print(
    f"Torrent name: {transmissionClient.get_torrents()[1].name}\nTorrent data location: {transmissionClient.get_torrents()[1].download_dir}")
newPath = input("Please enter the FULL PATH of the downloaded file: ")

torrentId = transmissionClient.get_torrents()[1].id
filename = os.path.basename(newPath)
folderPath = pathlib.Path(os.path.dirname(newPath))
print(f"After renaming, id: {torrentId} Torrent name: {filename}\nTorrent data location: {folderPath}")
if input("Validate? (y/N)").lower() == "y":
    transmissionClient.rename_torrent_path(torrent_id=torrentId, location=folderPath, name=filename)
    print(
    f"Torrent name: {transmissionClient.get_torrents()[1].name}\nTorrent data location: {transmissionClient.get_torrents()[1].download_dir}")
else:
    print("Skipping")