SPLAYERC=/home/jcmarsh/research/static_libplayerc
INC=-I$(SPLAYERC)/ -I$(SPLAYERC)/player_build/ -I$(SPLAYERC)/player_include/

all: basic

basic:
	diet gcc -nostdinc -m32 $(INC) -o basic basic.c $(SPLAYERC)/libplayerc.a

clean:
	rm -f basic
