#!/bin/bash

# Script's variables
SCRIPT_NAME=${0##*/};
SCRIPT_TIME=$(date "+%Y%m%d_%H%M%S");
SCRIPT_UNIQUE_NAME=${SCRIPT_NAME%.sh}.${SCRIPT_TIME};
SCRIPT_LOGFILE=/home/pi/git/com.zwolf.raspberrypi/dlss/logs/${SCRIPT_UNIQUE_NAME}.log;
SCRIPT_ERRORFILE=/home/pi/git/com.zwolf.raspberrypi/dlss/logs/${SCRIPT_UNIQUE_NAME}.err;
SCRIPT_EXECUTOR=$(whoami);
VERBOSE="false";

URL_REGEX="^\(https\?\):\/\/[A-Za-z0-9\+&@#/%?=~_|\!:,.;-]*";
COMMENT_REGEX="^#";
DEFAULT_INPUT="/home/pi/git/com.zwolf.raspberrypi/dlss/urls.txt";

INPUT_FILE="";
INPUT_FILE_BACKUP=logs/${SCRIPT_UNIQUE_NAME}.txt;
URLS=();
OUTPUT_FOLDER="/srv/dev-disk-by-uuid-FE5A2CD05A2C880B/NNLK_NEW/ZWOLF_HOME/_Nanalka/new/dlss";
NUMBER_OF_URLS="";

TOTAL_TIME="";
ERRORS=0;
SUCCESS=0;

################################################

# Functions

function printUsage() {
    echo "  Usage:  ${SCRIPT_NAME} [-i INPUT_FILE] [-o OUTPUT_FOLDER] [-v]";
    echo "    INPUT_FILE    - Path to an existing file containing video URLs.";
    echo "    OUTPUT_FOLDER - Optional parameter to a directory to place the files into.";
}

function logInfo() {
    my_msg=$1;
    my_log="  [INFO  $(date '+%Y.%m.%d %H:%M:%S')] ${my_msg}";

    echo "${my_log}";
    echo "${my_log}" >> ${SCRIPT_LOGFILE} &
}

function logError() {
    my_msg=$1;
    my_log="  [ERROR $(date '+%Y.%m.%d %H:%M:%S')] ${my_msg}";

    echo "${my_log}";
    echo "${my_log}" >> ${SCRIPT_LOGFILE} &
}

function verbose() {
    if [[ "true" == ${VERBOSE} ]]
    then
        my_msg=$1;
        my_log="  [VERBOSE $(date '+%Y.%m.%d %H:%M:%S')] ${my_msg}";

        echo "${my_log}";
        echo "${my_log}" >> ${SCRIPT_LOGFILE} &
    fi
}

#
# Sets variables and performs input parameter validations
#
function initScript() {

    # Getting parameters
    while getopts 'i:o:v' option
    do
        case ${option} in
            i) INPUT_FILE="${OPTARG}";
               ;;
            o) OUTPUT_FOLDER="${OPTARG}";
               ;;
            v) VERBOSE="true";
               ;;
            ?) printUsage;
               exit 1;
               ;;
        esac
    done

    shift "$(($OPTIND - 1))"

    # Input file validation
    if [[ ${INPUT_FILE} == "" ]]
    then
        verbose "No input file provided, using default file: '${DEFAULT_INPUT}'";
        INPUT_FILE=${DEFAULT_INPUT};
    fi

    if [[ ! -f ${INPUT_FILE} ]]
    then
        echo "  Input file does not exist: ${INPUT_FILE}";
        printUsage;
        exit 1;
    fi

    # Setting NUMBER_OF_URLS and creating log files
    URLS=(`grep -e "${URL_REGEX}" ${INPUT_FILE} | sort -u`);

    NUMBER_OF_URLS=${#URLS[@]};
    > ${SCRIPT_LOGFILE}
    > ${SCRIPT_ERRORFILE}
    cat ${INPUT_FILE} > ${INPUT_FILE_BACKUP}
    chmod 777 ${SCRIPT_LOGFILE} ${SCRIPT_ERRORFILE} ${INPUT_FILE_BACKUP}
}

function takeScreenshots() {
    start=`date "+%s"`;
    counter=0;

    for ENTRY in "${URLS[@]}"
    do
        ((counter++));

        if [[ "${ENTRY}" == "" ]]
        then
            verbose "Skipping empty entry";
            continue;
        fi

        if [[ ${ENTRY} =~ ${COMMENT_REGEX} ]]
        then
            verbose "Skipping commented entry: '${ENTRY}'";
            continue;
        fi

        OIFS=${IFS};
        IFS=",";
        read -r -a array <<< "${ENTRY}";
        IFS=${OIFS};

        URL=${array[0]};
        WIDTH=${array[1]};
        HEIGHT=${array[2]};
        FILE_NAME=${array[3]};
        FILE_PATH=${array[4]};

        OUTPUT_FILE="${FILE_NAME}-${SCRIPT_TIME}.png";

        logInfo "(${counter} / ${NUMBER_OF_URLS}) Taking screenshot of: '${URL}'";
        verbose "  ${WIDTH} x ${HEIGHT} => ${OUTPUT_FILE}";
        chromium-browser --window-size="${WIDTH},${HEIGHT}" --screenshot --hide-scrollbars --headless "${URL}" > /dev/null 1>/dev/null 2>/dev/null
        chmod 777 screenshot.png;

        if [ ! -d "${OUTPUT_FOLDER}/${FILE_PATH}" ]
        then
            mkdir -p "${OUTPUT_FOLDER}/${FILE_PATH}";
        fi

        sudo mv "screenshot.png" "${OUTPUT_FOLDER}/${FILE_PATH}/${OUTPUT_FILE}";
    done

    end=`date "+%s"`;
    TOTAL_TIME=$((end - start));
}

function printSummary() {
    totalTime=`date -ud "@${TOTAL_TIME}" "+%H:%M:%S"`;

    echo " ";
    echo "  ----------------------------------------------------";
    echo "  SUMMARY";
    echo "  ----------------------------------------------------";
    echo "  Input URLs:    ${NUMBER_OF_URLS}";
    echo "  Total time:    ${totalTime}"
    echo "  Log File:      ${SCRIPT_LOGFILE}"
    echo "  Input backup:  ${INPUT_FILE_BACKUP}"
    echo "  ----------------------------------------------------";
}

################################################

# Main

initScript $@;
takeScreenshots;
printSummary;
