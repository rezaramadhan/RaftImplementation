#!/bin/bash

#cek apakah direktori /etc/apt/apt.conf.d ada, kalo ga ada bikin
function cekDir {
	DIR=/etc/apt/apt.conf.d
	if [[ ! -d ${DIR} ]] ; then
		mkdir -p ${DIR}
		printf "*Membuat direktori ${DIR}*\n\n"
	fi
}

#tampilan awal script
function showAwal {
	printf "=================================\n"
	printf "        Proxy Setter v1.0\n"
	printf "=================================\n"
	printf "\n"
	printf "Apakah yang akan anda lakukan?\n"
	printf "1. Set Proxy\n"
	printf "2. Unset Proxy\n"
	printf "Pilihan anda: "
}

#set proxy
function setproxy {
	printf "Username: "
	read USER
	printf "Password: "
	read -s PASS
	ISI="Acquire::http::Proxy \"http://${USER}:${PASS}@cache.itb.ac.id:8080\";;
		Acquire::https::Proxy \"http://${USER}:${PASS}@cache.itb.ac.id:8080\";;
		Acquire::ftp::Proxy \"http://${USER}:${PASS}@cache.itb.ac.id:8080\";;"
	touch ${DIR}${FILENAME}
	echo ${ISI} > ${DIR}${FILENAME}
	THISHOST=$(hostname)
	printf "\nSetting proxy untuk komputer: ${THISHOST} berhasil!\n"
}
#unset proxy
function unsetproxy {
	rm ${DIR}${FILENAME}
	THISHOST=$(hostname)
	printf "\nSetting proxy untuk komputer: ${THISHOST} berhasil dihapus\n"
}
#minta input ke user, apakah mau set atau unset proxy
function proses {
	read PIL
	FILENAME=008proxy
	DIR=/etc/apt/apt.conf.d/
	if [[ ${PIL} == '2' ]] ; then #remove file
		unsetproxy
	elif [[ ${PIL} == '1' ]] ; then #set proxy
		setproxy
	else
		printf "Pilihan tidak valid\n"
		exit -1
	fi
}

#Bagian utama script
cekDir
showAwal
proses
