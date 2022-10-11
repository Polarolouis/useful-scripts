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

if verbose:
    print(f"RPC Version: {transmissionClient.rpc_version}")

incompleteTorrentsList = [
    torrent for torrent in transmissionClient.get_torrents() if torrent.available != 100.0]

lenIncompleteList = len(incompleteTorrentsList)

for index, incompleteTorrent in enumerate(incompleteTorrentsList):
    print(f"---{index:03d}/{lenIncompleteList} | {index/lenIncompleteList*100:.2f}%---")

    # Extracting torrent ID, we'll use it because it doesn't change
    torrentId = incompleteTorrent.id

    print(
        f"Torrent name: {transmissionClient.get_torrent(torrentId).name}\nTorrent data location: {transmissionClient.get_torrent(torrentId).download_dir}")
    newPath = input("Please enter the FULL PATH of the downloaded file: ")

    filename = os.path.basename(newPath)
    folderPath = pathlib.Path(os.path.dirname(newPath))
    print(folderPath)
    print(
        f"After renaming, id: {torrentId} \nNew torrent name: {filename}\nNew torrent data location: {folderPath}")
    if input("Validate? (y/N)").lower() == "y":

        # Changing the directory containing the data
        transmissionClient.move_torrent_data(
            ids=torrentId, location=folderPath)

        # Retrieving the torrent name to change it
        fileToRename = transmissionClient.get_torrent(torrentId).name.strip()
        # If we do not strip it won't work
        # the problem seems to occur because of trailing whitespaces

        if verbose:
            print(fileToRename)
            print(transmissionClient.get_torrent(torrentId))

        # Renaming the torrent
        transmissionClient.rename_torrent_path(
            torrentId, fileToRename, filename)
        print(
            f"Torrent name: {transmissionClient.get_torrent(torrentId).name}\nTorrent data location: {transmissionClient.get_torrent(torrentId).download_dir}")
        if verbose:
            print(
                f"Verifying {transmissionClient.get_torrent(torrentId).name} data on {transmissionClient.get_torrent(torrentId).download_dir}.")
        try:
            transmissionClient.verify_torrent(torrentId)
        except Exception as e:
            print(
                f"An error occured while verifying the data on the provided download directory : {e}")
    else:
        print("Skipping")
