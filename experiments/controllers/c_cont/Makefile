RESEARCH=/home/jcmarsh/research
SPLAYERC=$(RESEARCH)/static_libplayerc
PLAYERC=$(RESEARCH)/player
LIBCDIR=$(RESEARCH)/dietlibc-0.33/bin-i386
INC=-I$(SPLAYERC)/ -I$(SPLAYERC)/player_build/ -I$(SPLAYERC)/player_include/
R_INC=-I$(PLAYERC)/ -I$(PLAYERC)/build/

all: regular

diet:
	diet gcc -nostdinc $(INC) -o basic basic.c $(SPLAYERC)/libplayerc.a $(LIBCDIR)/dietlibc.a $(LIBCDIR)/librpc.a $(LIBCDIR)/libm.a
	diet gcc -nostdinc $(INC) -o planner_cmd planner_cmd.c $(SPLAYERC)/libplayerc.a $(LIBCDIR)/dietlibc.a $(LIBCDIR)/librpc.a $(LIBCDIR)/libm.a

regular:
	gcc $(INC) -o basic basic.c -lplayerc
	gcc $(INC) -o planner_cmd planner_cmd.c -lplayerc

clean:
	rm -f basic
	rm -f planner_cmd
