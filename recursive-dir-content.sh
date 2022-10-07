#!/bin/bash

    # A recursive content lister
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


usage () {
    echo "Description: $(basename "$0") is an utility script to list the files recursively in a folder." 
    echo 
    echo "Usage: "
    echo "$(basename "$0") ROOT_DIRECTORY LIST_FILE"
    echo ""
    echo "Arguments:"
    echo "ROOT_DIRECTORY: the root folder to explore"
    echo "LIST_FILE: the output file to which the list of files will be written"
}

dir_list () {
    echo "-Folder $1-"

    for FILE in $1/* # Loop over the files in the folder given as first arg
    do
        echo "Scanning: $FILE"

        # Is the file to change a directory ?
        if [[ -d "$FILE" ]]; then
        # If it is we loop over its content
            echo "$FILE is actually a directory !"
            dir_list $FILE $2
        else
            echo "$FILE is not a directory ! Adding it to the list"
            # Writing the file in the output list
            echo $FILE >> $2
        fi
    done
    echo "-----------------------------------------------"
}

# This line to go over dotfiles and dotfolders
shopt -s dotglob

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "ERROR: Missing at least one of the required arguments !"
    echo ""
    usage
else
    echo "Creating/emptying the previous list"
    if [ -f "$2" ]; then
        echo "$2 exists, backing it up to $2.old"
        if [ -f "$2.old" ]; then
            echo "$2.old exists already ! Deleting it"
            rm $2.old
        fi
        mv $2 $2.old
    fi
    touch $2
    dir_list $1 $2
fi