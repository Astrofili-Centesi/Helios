#!/bin/bash 
# Meglio installare una ramdisk sudo mount -t tmpfs -o size=100M tmpfs /home/thomas/Scrivania/ramdisk/

# carica il file di configurazione
source /home/helios/helios/helios.cfg

logger -t Helios Start processing 
logger -t Helios work_path ${work_path}
logger -t Helios ramdisk_path ${ramdisk_path}

if [ $keyon -eq 1 ]
then
	# legge la data
	dt="$(date -u -Is)"
	
	#controllo amplificatore
	pacmd set-source-port 1 analog-input-linein
	pacmd set-source-volume 1 ${volacq}
	
	# acquisizione segnale 
	rec -q -r192k -c 2 $ramdisk_path/input.wav trim 1 $lenacq

	logger -t Helios Rec done

	cp $ramdisk_path/input.wav $ramdisk_path/input_all.wav
	sox -q $ramdisk_path/input.wav $ramdisk_path/l.wav remix 1
	sox -q $ramdisk_path/input.wav $ramdisk_path/r.wav remix 2
	sox -q -m -v 1 $ramdisk_path/l.wav -v -1 $ramdisk_path/r.wav $ramdisk_path/input.wav

	logger -t FFT calc
	"${work_path}/venv/bin/python" "${work_path}/Helios/scripts/fft_extractor.py" --output "${work_path}/fftnew.csv" --window flattop "${ramdisk_path}/input.wav" "${dt}" 8192
   
	#RMS del segnale
	sox -q $ramdisk_path/input.wav -n stats 2> $ramdisk_path/app.txt
	dvrms="$(sed -n 6p ${ramdisk_path}/app.txt | cut -c 15-20)"
	dvrms=$(bc <<< "scale=2; $dvrms - 40")
    
	# filtraggio e misura rms dei canali e registrazione su db
	cs=""

	printf "$dt" >> ${work_path}/db.csv
	for (( i=0; i<${#freq[@]}; i++))
	do
	   sox -q $ramdisk_path/input.wav $ramdisk_path/input1.wav bandpass ${freq[$i]} ${lb[$i]}
	   sox -q -v ${gain[$i]} $ramdisk_path/input1.wav -n bandpass ${freq[$i]} ${lb[$i]} stats 2> $ramdisk_path/app.txt
	  	   
	   # lettura canale orizzontale in dB
	   dva="$(sed -n 5p ${ramdisk_path}/app.txt | cut -c 15-20)"
	   
	   if (( $(echo "$dva > 0.0" |bc -l) ))
	   then
	    dva=0
	   fi
	   printf ",$dva" >> ${work_path}/db.csv
	   
	   cs=$cs"ch"$i"="$dva','
	   
	done
	if (( $(echo "$dvrms > 0.0" |bc -l) ))
	   then
	    dvrms=0
	   fi
	printf ",$dvrms" >> ${work_path}/db.csv
	printf "\n" >> ${work_path}/db.csv
	tail -n 1 ${work_path}/db.csv >> ${work_path}/db_delta.csv
	
	
	#influxdb
	#cs=${cs::-1}" $(date +%s)000000000"
	#curl -s -X POST "http://www.matteofortini.it:8086/api/v2/write?org=96987f3490132173&bucket=helios&precision=ns" -H "Authorization: Token M-14tiwiA7pnYXs3I_zreZxwW0-_RliQ-aOKt8ofLEaIW8xqX6Rt9otcYTE1NevsUnl5fvE3bi25r6cxjB68yQ==" -H "Content-Type: text/plain; charset=utf-8" -H "Accept: application/json" -d "helios,sensorID=Helios $cs"
    #printf "$cs\n" >> ${work_path}/curl_db.txt
		
	#creazione spettrogramma ricordarsi 
    sox -q $ramdisk_path/input.wav -n spectrogram -o $ramdisk_path/spectrogram.png -Y2000 -m -h -t "Astrofili Centesi - Helios VLF" -c "$(date)"
	
	logger -t Helios lftp
	#su ftp.astrofili.it
    lftp -c "open ftp.astrofilicentesi.it:21; user '15738057@aruba.it' 'Pjer658_r94!jfsS'; cd www.astrofilicentesi.it/Appoggio; put $ramdisk_path/spectrogram.png; bye"
	
	#esegue il git ai 00 e ai 30 di ogni ora
	if [ $(date +%M) -eq 00 ] || [ $(date +%M) -eq 30 ]
	then 
	     
	   #git
	   logger -t Helios git pull
	   cd ${work_path}/Helios
	   git reset --hard HEAD
	   git clean -fxd
	   git pull --rebase
	   
	   #cp ../db.csv .
	   cat ../db_delta.csv >> ./db.csv
	   cp ../freq.csv .

	   logger -t Helios Store fft
	   "${work_path}/venv/bin/python" "${work_path}/Helios/scripts/process_fft.py"
	   rm ../fftnew.csv

	   #
	   git add db.csv
	   git add freq.csv
	   git add fft.csv
	   git add fft
	   
	   logger -t Helios git commit
	   git commit -m "Update $(date -Is)"
	   git push
	   logger -t Helios git push
	   cd ..
	   rm ./db_delta.csv

     fi
fi

