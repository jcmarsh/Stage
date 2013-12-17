RESEARCH=/home/jcmarsh/research
SPLAYERC=$(RESEARCH)/static_libplayerc
LIBCDIR=$(RESEARCH)/dietlibc-0.33/bin-i386
INC=-I$(SPLAYERC)/ -I$(SPLAYERC)/player_build/ -I$(SPLAYERC)/player_include/

all: basic

basic:
	diet gcc -nostdinc $(INC) -o basic basic.c $(SPLAYERC)/libplayerc.a $(LIBCDIR)/dietlibc.a $(LIBCDIR)/librpc.a $(LIBCDIR)/libm.a

clean:
	rm -f basic
