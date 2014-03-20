module sizes
  integer,parameter :: rk0=selected_real_kind(5,10)    ! single precision
  integer,parameter :: rk=selected_real_kind(10,40)    ! double precision
  integer,parameter :: rk2=selected_real_kind(30,200)  ! quadruple precision
  integer,parameter :: MAXBUF=200
end module sizes