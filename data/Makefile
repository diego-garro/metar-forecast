YEAR=2022
STATION=mrpv

download:
	# January
	get-metars -i $(YEAR)-01-01 -f $(YEAR)-01-31T23:59:00 -o $(STATION)
	cat metar.txt > $(STATION)/$(YEAR).txt
	sleep 20
	# February
	get-metars -i $(YEAR)-02-01 -f $(YEAR)-02-28T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# March
	get-metars -i $(YEAR)-03-01 -f $(YEAR)-03-31T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# April
	get-metars -i $(YEAR)-04-01 -f $(YEAR)-04-30T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# May
	get-metars -i $(YEAR)-05-01 -f $(YEAR)-05-31T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# June
	get-metars -i $(YEAR)-06-01 -f $(YEAR)-06-30T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# July
	get-metars -i $(YEAR)-07-01 -f $(YEAR)-07-31T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# August
	get-metars -i $(YEAR)-08-01 -f $(YEAR)-08-31T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# September
	get-metars -i $(YEAR)-09-01 -f $(YEAR)-09-30T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# October
	get-metars -i $(YEAR)-10-01 -f $(YEAR)-10-31T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# November
	get-metars -i $(YEAR)-11-01 -f $(YEAR)-11-30T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	sleep 20
	# December
	get-metars -i $(YEAR)-12-01 -f $(YEAR)-12-31T23:59:00 -o $(STATION)
	cat metar.txt >> $(STATION)/$(YEAR).txt
	rm metars.txt
