RESEARCH=/home/jcmarsh/research
SPLAYERC=$(RESEARCH)/static_libplayerc
LIBCDIR=$(RESEARCH)/dietlibc-0.33/bin-i386
INC_DIET=-I$(SPLAYERC)/ -I$(SPLAYERC)/player_build/ -I$(SPLAYERC)/player_include/

all: triple

triple:
	gcc -o triple `pkg-config --cflags playerc` triple.c `pkg-config --libs playerc`

triple_dietlibc:
	diet gcc -nostdinc $(INC_DIET) -o triple triple.c $(SPLAYERC)/libplayerc.a $(LIBCDIR)/dietlibc.a $(LIBCDIR)/librpc.a $(LIBCDIR)/libm.a

clean:
	rm -f triple
