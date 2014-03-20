F90=mpifort
FFLAGS=-O3
LDFLAGS=
# I'm doing my homework on windows, thus program filenames are .exe
PROG=traveller.exe
OBJ=sizes.o $(PROG:.exe=.o)

all: $(OBJ) $(PROG)
	
%.exe: %.o
	$(F90) $(LDFLAGS) -o $@ $?

%_O0.o: %.f90
	$(F90) -O0 -c -o $@ $<
	
%_O1.o: %.f90
	$(F90) -O1 -c -o $@ $<
	
%_O2.o: %.f90
	$(F90) -O2 -c -o $@ $<

%_O3.o: %.f90
	$(F90) -O3 -c -o $@ $<
	
%.o: %.f90
	$(F90) $(FFLAGS) -c -o $@ $<

clean:
	rm $(OBJ) $(PROG) sizes.mod