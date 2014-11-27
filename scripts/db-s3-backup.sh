#!/bin/bash
# Shell script to backup MySql database

set -e

# CONFIG - Only edit the below lines to setup the script
# ===============================
 
S3Bucket="sarpam-meddb" # S3 Bucket
 
# Space-separated list of databases to backup
DBS="med_db"
 
# DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING
# ===============================
 
# Linux bin paths, change this if it can not be autodetected via which command
POSTGRESDUMP="sudo su postgres - -c $(which pg_dump)"
GZIP="$(which gzip)"
 
# Get data in yyyy-mm-dd format
NOW="$(date +"%Y-%m-%d")"
 
# Backup Dest directory, change this if you have someother location
BACKUP_ROOT="/var/backups/med_db"
BACKUP_PREFIX="med_db-$NOW"
 
# Main directory where backup will be stored
DEST="$BACKUP_ROOT/$BACKUP_PREFIX"
 
# Get hostname
HOST="$(hostname)"
 
# File to store current backup file
FILE=""
 
[ ! -d $DEST ] && mkdir -p $DEST || :
 
for db in $DBS
do
  FILE="$DEST/$db.$HOST.$NOW.gz"

  echo "Backing up $db to $FILE"

  # dump database to file and gzip
  date --rfc-3339=ns
  $POSTGRESDUMP $db | $GZIP -9 > $FILE
  CODE=${PIPESTATUS[0]}
  date --rfc-3339=ns

  if [ $CODE -ne 0 ]; then
    echo "pg_dump failed"
    exit 1
  fi

  echo "Dump complete"

  ls -l $FILE
done
 
# copy mysql backup directory to S3
echo "Syncing with S3"
s3cmd put -v $FILE s3://$S3Bucket/$BACKUP_PREFIX/

echo "Finished. Bye."
