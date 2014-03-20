program travel
    use sizes
    !use mpi
    implicit none
    include 'mpif.h'
    
    integer,parameter            :: bufsize=200                     ! Buffer for strings
    integer,parameter            :: unit_number=10                  ! Unit number for configuration file
    
    real(kind=rk),allocatable    :: x(:),y(:)                       ! Coordinate arrays for cities (ncities)
    integer,allocatable          :: population(:,:)                 ! Population array (ncities, pop_size)
    integer,allocatable          :: result_population(:,:)          ! Population array (ncities, pop_size) for results
    integer,allocatable          :: picked(:)                       ! Utility array for temporary population holding
    real(kind=rk),allocatable    :: energies(:)                     ! Energies of routes
    real(kind=rk),allocatable    :: result_energies(:)              ! Energies of best routes
    real(kind=rk)                :: Esum                            ! Sum of all energies for the partition function
    real(kind=rk)                :: cumsum                          ! Cumulative sum of all energies for the partition function
    real(kind=rk)                :: T                               ! Temperature for the partition function
    real(kind=rk)                :: T_old                           ! Temperature changes
    real(kind=rk)                :: lmin                            ! Min length of route
    real(kind=rk)                :: lmax                            ! Max length of route
    
    integer                      :: seed,seed_size                  ! Seed 
    integer,allocatable          :: seed_array(:)                   ! Array for seeds
    real(kind=rk)                :: u_r                             ! Random real
    integer                      :: u_i                             ! Random integer
    
    integer                      :: pop_size                        ! Population size
    integer                      :: migration_rate                  ! Migration rate
    integer                      :: migration_n                     ! Number of routes to migrate
    integer                      :: n_cities                        ! Number of cities
    integer                      :: printstep                       ! Print step rate
    real(kind=rk)                :: mutation_p                      ! Mutation probability
    integer                      :: i,j,k,l                         ! Index integers
    integer                      :: ex,ex1,ex2                      ! Integers for existence checking
    integer                      :: n_picked                        ! Number of cities that remain to be picked
    integer                      :: city0, city1, city2             ! City number integers
    real(kind=rk)                :: r1,r2                           ! City distance variables
    integer                      :: n, steps                        ! Time step integers
    
    integer                      :: n_args                          ! Number of command line arguments
    character(len=bufsize)       :: arg                             ! Char array for command line arguments
    
    integer                      :: rank                            ! Rank of this task
    integer                      :: next_rank,prev_rank             ! Rank of next and previous tasks
    integer                      :: ntasks                          ! Number of tasks
    integer                      :: ioerr                           ! I/O error integer
    integer                      :: mpierr                          ! MPI error integer
    integer                      :: mpistatus(MPI_STATUS_SIZE)      ! MPI status array
    
    real(kind=rk)                :: t1,t2

    ! -------------------------------------------------------------------------
    ! MPI initiation
    
    call mpi_init(mpierr)
    if (mpierr/=mpi_success) then
        print *,'MPI initialization failed.'
        stop
    end if
    call mpi_comm_size(MPI_COMM_WORLD,ntasks,mpierr)
    call mpi_comm_rank(MPI_COMM_WORLD,rank,mpierr)
    
    ! Calculate next and previous task ranks 
    next_rank = modulo(rank+1,ntasks)
    prev_rank = modulo(rank-1,ntasks)
    
    ! -------------------------------------------------------------------------
    ! Input I/O and parameter distribution
    
    ! Get the input filename
    n_args = command_argument_count()
    if (n_args /= 1) then
        if (rank == 0) then
            call get_command_argument(0,arg)
            print *,'Usage: ', trim(arg),' cityfile'
            call mpi_Finalize()
            stop
        else
            call mpi_Finalize()
            stop
        end if
    end if
    
    ! Root process reads input file
    
    if (rank == 0) then
        t1 = MPI_Wtime()

        call get_command_argument(1,arg)
        
        ! Open input file
        open(unit=unit_number, file=arg, status='old', action='read', iostat=ioerr)
        
        ! Check that the file opened properly
        if (ioerr /= 0) then
            print *,'Error opening input : ', trim(arg)
            go to 101
        end if
        
        ! Data should be like this:
        !
        ! pop_size
        ! seed
        ! steps
        ! printstep
        ! migration_rate
        ! migration_n
        ! mutation_p
        ! n_cities
        !
        ! x1 y1
        ! x2 y2
        ! ...
        ! Anything beyond first columns is a comment
        
        ! Program does not check for invalid input numbers, e.g. if population size is negative or less than three
        ! I didn't want to write so many if-clauses and thus setting proper values is up to the user.
        
        ! Read parameters, in case of errors go to the end and notify user
        read(unit_number, *, iostat=ioerr) pop_size
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) seed
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) steps
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) printstep
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) migration_rate
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) migration_n
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) mutation_p
        if (ioerr /= 0) go to 101
        read(unit_number, *, iostat=ioerr) n_cities
        if (ioerr /= 0) go to 101
        ! Allocate cities and read them in
        allocate(x(n_cities), y(n_cities), stat=ioerr)
        if (ioerr /= 0) go to 101
        do i=1,n_cities
            read(unit_number, *, iostat=ioerr) x(i), y(i)
            ! Check for invalid data or file ends
            if ((ioerr /= 0) .and. (i<n_cities)) go to 100
        end do
        ! Check for invalid data in the last index
        if (ioerr>0) go to 100
        
        ! Everything went ok. Give user a rundown on inputs
        print '(a14)','Using inputs:'
        print '(a14,1i8)','pop_size      =',pop_size
        print '(a14,1i8)','seed          =',seed
        print '(a14,1i8)','steps         =',steps
        print '(a14,1i8)','printstep     =',printstep
        print '(a14,1i8)','migration_rate=',migration_rate
        print '(a14,1i8)','migration_n   =',migration_n
        print '(a14,1f8.3)','mutation_p    =',mutation_p
        print '(a14,1i8)','n_cities      =',n_cities
        
        ! Set ioerr to ok and go to end.
        ioerr = 0
        go to 102
        
        100 deallocate(x,y)
        101 print *,'Invalid input file!'
        102 close(unit_number)
        
    end if
    
    ! Broadcast ioerr and check end program if something was amiss
    call MPI_Bcast(ioerr, 1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    if (ioerr /= 0) then
        call MPI_Finalize()
        stop
    end if
    
    ! Input is loaded, time to start simulations
    
    ! Broadcast input to all tasks
    call MPI_Bcast(pop_size,        1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(seed,            1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(steps,           1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(printstep,       1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(migration_rate,  1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(migration_n,     1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(mutation_p,      1, MPI_DOUBLE_PRECISION,  0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(n_cities,        1, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
        
    ! Allocate needed arrays
    
    if (rank /= 0) then
        allocate(x(n_cities), y(n_cities), picked(n_cities), &
        population(n_cities,pop_size), energies(pop_size), stat=ioerr)
    else
        allocate(picked(n_cities), population(n_cities,pop_size), result_population(n_cities,ntasks),&
        energies(pop_size), result_energies(ntasks), stat=ioerr)
    end if
    
    ! Stop if program ran out of memory
    
    if (ioerr /= 0) then
        print '(a,i5,a)', 'Warning: rank ',rank,' could not allocate memory!'
        call MPI_Finalize()
        stop
    end if
    
    ! Send city coordinates to every task
    
    call MPI_Bcast(x,    n_cities, MPI_DOUBLE_PRECISION,  0, MPI_COMM_WORLD, mpierr)
    call MPI_Bcast(y,    n_cities, MPI_DOUBLE_PRECISION,  0, MPI_COMM_WORLD, mpierr)
        
    ! -------------------------------------------------------------------------
    ! Initial population creation
    
    ! Set unique seeds for each and every process
    call random_seed(size=seed_size)
    allocate(seed_array(seed_size))
    do i=1,seed_size
        seed_array(i) = i + seed + rank * seed_size
    end do
    call random_seed(put=seed_array)
        
    ! Set initial values
    population     = 0
    energies    = 0
    lmin        = HUGE(lmin)
    lmax        = 0
    do j=1,pop_size
        ! Periodic conditions mean that every loop can start from city number 1
        population(1,j) = 1
        ! Picked array contains cities that haven't been picked.
        ! This is done in order to hasten initialization with large number of cities.
        n_picked=n_cities-1
        do i=1,n_picked
            picked(i) = i+1
        end do
        
        do i=2,n_cities
            ! Pick a city from those that have not been picked yet
            call random_number(u_r)
            u_i = ceiling(n_picked*u_r)
            k = picked(u_i)
            
            population(i,j) = k
            ! Remove chosen sity from picked array and move others down the queue
            n_picked = n_picked - 1
            do l=u_i,n_picked
                picked(l) = picked(l+1)
            end do
            
            ! Add distance between cities to the route length
            energies(j) = energies(j) + distance(population(i,j), population(i-1,j), x, y)        
        end do
        
        ! Once route is done, add periodic distance
        energies(j) = energies(j) + distance(population(1,j), population(n_cities,j), x, y)
        
        ! Check if we have a new max or min length
        if (energies(j) > lmax) then
            lmax = energies(j)
        else if (energies(j) < lmin) then
            lmin = energies(j)
        end if
    end do
    
    ! Calculate temperature and map route lengths to route energies.
    ! Add them to the sum of energies.
    T         = lmax-lmin
    Esum    = 0.0
    do i=1,pop_size
        energies(i) = exp(-energies(i)/T)
        Esum        = Esum + energies(i)
    end do
        
    ! -------------------------------------------------------------------------
    ! Simulation
    
    ! Pick first route to be replaced
    
    l = minloc(energies,dim=1)
    
    do n=1,steps    
    
        ! Kill of the worst route and remove it from mating pool
        
        Esum    = Esum - energies(l)
        energies(l)    = 0
        population(1:n_cities, l)     = 0
        
        ! Pick routes to mate based on their energies
        cumsum = 0
        call random_number(u_r)
        u_r = Esum*u_r            
        
        do i=1,pop_size
            cumsum = cumsum+energies(i)
            if (cumsum > u_r) then
                j = i
                exit
            end if
        end do
        k = j
        do while(k==j)
            cumsum = 0
            call random_number(u_r)
            u_r = Esum*u_r
            do i=1,pop_size
                cumsum = cumsum+energies(i)
                if (cumsum > u_r) then
                    k = i
                    exit
                end if
            end do
        end do
        
        ! Pick a starting city
        call random_number(u_r)
        if (u_r < 0.5) then
            population(1,l) = population(1,j)
        else
            population(1,l) = population(1,k)
        end if
                                
        ! Pick next cities
        do i=2,n_cities
            ! Get city numbers for this city (city0) and possible choices (city1 and city2)
            city0    = population(i-1,l)
            city1    = population(i,j)
            city2    = population(i,k)
            ! Get distances from city0 to city1 and city2 respectively
            r1     = distance(city0,city1,x,y)
            r2    = distance(city0,city2,x,y)
            ! Check whether city1 or city2 exist in the current route
            ex1    = exists(city1, i-1, population(1:n_cities,l))
            ex2 = exists(city2, i-1, population(1:n_cities,l))
            if (r1 < r2) then
                ! city1 was closer. If it doesn't exist in route, pick it and continue.
                if (ex1 /= 0) then
                    population(i, l)     = city1
                    energies(l)            = energies(l) + r1
                    cycle
                ! city1 was already in the route. If city2 doesn't exist, pick it and continue.
                else if (ex2 /= 0) then
                    population(i, l)     = city2
                    energies(l)            = energies(l) + r2
                    cycle
                end if
            else
                ! city2 was closer. If it doesn't exist in route, pick it and continue.
                if (ex2 /= 0) then
                    population(i, l)     = city2
                    energies(l)            = energies(l) + r2
                    cycle
                ! city2 was already in the route. If city1 doesn't exist, pick it and continue.
                else if (ex1 /= 0) then
                    population(i, l)     = city1
                    energies(l)            = energies(l) + r1
                    cycle
                end if
            end if
            ! Both cities were already in route. Pick a random one.
            ex = 0
            do while (ex==0)
                ! Pick a city from possible cities until one that doesn't exist in the route is found.
                call random_number(u_r)
                u_i = ceiling(n_cities*u_r)
                ex=exists(u_i, i-1, population(1:n_cities,l))
            end do
            population(i, l)    = u_i
            energies(l)            = energies(l) + distance(city0,u_i,x,y)
        end do
        ! Add periodic distance.
        energies(l)    = energies(l) + distance(population(1,l), population(n_cities,l), x,y)
        
        ! Check whether to do a mutation or not.
        call random_number(u_r)
        if (u_r < mutation_p) then
            ! Pick a city and change its position with the next one in the route.
            call random_number(u_r)
            j = ceiling(n_cities*u_r)
            city1    = population(j,l)
            ! Previous city
            i = modulo(j-2,n_cities)+1
            city0    = population(i,l)
            ! Next city
            k = modulo(j,n_cities)+1
            city2    = population(k,l)
            ! Remove distance between j-1 and j and add distance between j-1 and j+1
            energies(l)            = energies(l) - distance(city0,city1,x,y)
            energies(l)            = energies(l) + distance(city0,city2,x,y)
            ! Next city from k
            i = modulo(j+1,n_cities)+1
            city0    = population(i,l)
            ! Remove distance between j+1 and j+2 and add distance between j and j+2 
            energies(l)            = energies(l) - distance(city0,city2,x,y)
            energies(l)            = energies(l) + distance(city0,city1,x,y)
            population(j,l)    = city2
            population(k,l) = city1
        end if
        
        ! Map distances to energies and add the energy        
        energies(l)    = exp(-energies(l)/T)
        Esum        = Esum + energies(l)
        
        ! Check migration condition
        if (modulo(n,migration_rate) == 0) then
            ! Do a number of migrations. Split population to strides.
            do j=0,migration_n-1
                ! Pick maximum location from each stride.
                i = (maxloc(energies(1+j:pop_size:migration_n),dim=1)-1)*migration_n + j + 1
                picked     = population(1:n_cities,i)
                cumsum    = -T*log(energies(i))
                Esum    = Esum - energies(i)
                ! Send route and its energy.
                call MPI_Send(picked, n_cities, MPI_INTEGER, next_rank, 0, MPI_COMM_WORLD, mpierr)
                call MPI_Recv(population(1:n_cities,i), n_cities, MPI_INTEGER, prev_rank, 0, MPI_COMM_WORLD, mpistatus, mpierr)
                call MPI_Send(cumsum, 1, MPI_DOUBLE_PRECISION, next_rank, 0, MPI_COMM_WORLD, mpierr)
                call MPI_Recv(energies(i), 1, MPI_DOUBLE_PRECISION, prev_rank, 0, MPI_COMM_WORLD, mpistatus, mpierr)
                ! Recalculate energy
                energies(i) = exp(-energies(i)/T)
                Esum        = Esum + energies(i)
            end do
        end if
        
        ! Find the longest route for next round and get its length
        l        = minloc(energies,dim=1)
        lmax     = -T*log(energies(l))
        lmin    = -T*log(maxval(energies))
                
        ! Recalculate temperature
        T_old     = T
        T        = lmax-lmin
        if (T<0.1) then
            T = 0.1
        end if
        
        if (T_old /= T) then
            ! Temperature has changed, recalculate energies
                
            Esum        = 0
            do i=1,pop_size
                energies(i) = -T_old*log(energies(i))
            end do
        
            do i=1,pop_size
                energies(i) = exp(-energies(i)/T)
                Esum        = Esum + energies(i)
            end do
        end if
        
        if ((rank == 0) .and. (modulo(n,printstep) == 0)) then
            print '(a, i6, a, e10.3, a, e10.3, a, e10.3, a, e10.3)','t: ',n,' T: ',T, ' Esum: ', &
            Esum ,' min(L): ', -T*log(maxval(energies)), ' max(L): ', -T*log(minval(energies))
        end if
    end do
    ! Convert energies to lengths
    do i=1,pop_size
        energies(i) = -T*log(energies(i))
    end do
    i = minloc(energies,dim=1)

    ! Gather results to root process and print them
    call MPI_Gather(energies(i), 1, MPI_DOUBLE_PRECISION, result_energies, 1, MPI_DOUBLE_PRECISION, 0, MPI_COMM_WORLD, mpierr)
    call MPI_Gather(population(1:n_cities,i), n_cities, MPI_INTEGER, result_population, &
                    n_cities, MPI_INTEGER, 0, MPI_COMM_WORLD, mpierr)
    if (rank == 0) then
        t2 = MPI_Wtime()
        print *,'Shortest route of each task:'
        print '(100e13.3)',result_energies
        i = minloc(result_energies,dim=1)
        print *,'Time taken:'
        print *,t2-t1
        print *,'Best route:'
        print '(1000i6)',result_population(1:n_cities,i)
    end if
    
    ! -------------------------------------------------------------------------
    
    ! Finish
    call MPI_Finalize()
    stop
    
    contains
    
    integer function exists(city, max_i, cityarray)
        implicit none
        integer,intent(in)    :: city, max_i
        integer,intent(in)    :: cityarray(:)
        integer                :: city_i
        do city_i=1,max_i
            if (cityarray(city_i) == city) then
                exists = 0
                return
            end if
        end do
        exists = 1
        return
    end function exists
        
    real(rk) function distance(ix,jx,x_arr,y_arr)
        ! Calculate distance between two cities.
        implicit none
        integer,intent(in)    :: ix,jx
        real(rk),intent(in)    :: x_arr(:), y_arr(:)
        real(rk)            :: dx,dy
        dx  = (x_arr(ix)-x_arr(jx))
        dy    = (y_arr(ix)-y_arr(jx))
        distance = real(dx*dx + dy*dy, kind=rk)
        return
    end function distance
    
end program travel
