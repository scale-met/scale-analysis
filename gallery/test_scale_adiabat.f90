! mpif90 -shared -fPIC -o test_scale_adiabat.so test_scale_adiabat.f90 -J scale-5.3.3/include `nc-config --cflags` -L scale-5.3.3/lib -lscale `nc-config --libs`
! mpif90 -shared -fPIC -o test_scale_adiabat.so test_scale_adiabat.f90 -J scale-5.5.1/include `nc-config --cflags` -L scale-5.5.1/lib -lscale `nc-config --libs`

subroutine test_scale_adiabat(&
  TA,   &
  KA,   &
  KS,   &
  KE,   &
  IA,   &
  IS,   &
  IE,   &
  JA,   &
  JS,   &
  JE,   &
  Kstr, &
  TEMP, &
  PRES, &
  QV,   &
  QC,   &
  QR,   &
  QI,   &
  QS,   &
  QG,   &
  CZ,   &
  FZ,   &
  CAPE, &
  CIN,  &
  LCL,  &
  LFC,  &
  LNB,  &
  DENS_p, &
  TEMP_p, &
  BUOY_p, &
  QV_p &
)

  use scale
  use scale_precision
  !use scale_io
  !use scale_prof

  use scale_const, only: &
     PRE00 => CONST_PRE00, &
     Rdry  => CONST_Rdry,  &
     Rvap  => CONST_Rvap,  &
     CPdry => CONST_CPdry
  use scale_atmos_hydrometeor, only: &
     CPvap => CP_VAPOR, &
     CL    => CP_WATER, &
     CI    => CP_ICE
!  use scale_io, only: &
!     IO_get_available_fid
  use scale_atmos_saturation, only: &
     ATMOS_SATURATION_setup, &
     ATMOS_SATURATION_tdew_liq, &
     ATMOS_SATURATION_pote
  use scale_atmos_adiabat, only: &
     ATMOS_ADIABAT_setup, &
     ATMOS_ADIABAT_cape
  implicit none

  integer,  intent(in)  :: TA
  integer,  intent(in)  :: KA, KS, KE, Kstr
  integer,  intent(in)  :: IA, IS, IE
  integer,  intent(in)  :: JA, JS, JE
  real(RP), intent(in)  :: TEMP(IA,JA,KA,TA), PRES(IA,JA,KA,TA)
  real(RP), intent(in)  :: QV(IA,JA,KA,TA), QC(IA,JA,KA,TA), QR(IA,JA,KA,TA), QI(IA,JA,KA,TA), QS(IA,JA,KA,TA), QG(IA,JA,KA,TA)
  real(RP), intent(in)  :: CZ(KA), FZ(0:KA)

  real(RP), intent(inout) :: CAPE(IA,JA,TA), CIN(IA,JA,TA), LCL(IA,JA,TA), LFC(IA,JA,TA), LNB(IA,JA,TA)
  real(RP), intent(inout) :: DENS_p(IA,JA,KA,TA), TEMP_p(IA,JA,KA,TA), BUOY_p(IA,JA,KA,TA), QV_p(IA,JA,KA,TA)

  real(RP) :: POTT(IA,JA,KA,TA), DENS(IA,JA,KA,TA), QDRY(IA,JA,KA,TA)
  real(RP) :: Rtot(IA,JA,KA,TA), CPtot(IA,JA,KA,TA)
  real(RP) :: Tdew(IA,JA,KA,TA), POTE(IA,JA,KA,TA)

  logical :: converged

  integer :: i,j,k,t

!!!!!!!!!!!

  call SCALE_init

  call ATMOS_SATURATION_setup
  call ATMOS_ADIABAT_setup

  do t = 1, TA
  do k = 1, KA
  do j = 1, JA
  do i = 1, JA
     QDRY(i,j,k,t) = 1.0_RP - QV(i,j,k,t) - QC(i,j,k,t) - QR(i,j,k,t) - QI(i,j,k,t) - QS(i,j,k,t) - QG(i,j,k,t)
     Rtot(i,j,k,t)  =  Rdry * QDRY(i,j,k,t) +  Rvap * QV(i,j,k,t)
     CPtot(i,j,k,t) = CPdry * QDRY(i,j,k,t) + CPvap * QV(i,j,k,t) + CL * ( QC(i,j,k,t) + QR(i,j,k,t) ) &
     + CI * ( QI(i,j,k,t) + QS(i,j,k,t) + QG(i,j,k,t) )
     POTT(i,j,k,t) = TEMP(i,j,k,t) * ( PRE00 / PRES(i,j,k,t) )**( Rtot(i,j,k,t) / CPtot(i,j,k,t) )
     DENS(i,j,k,t) = PRES(i,j,k,t) / ( Rtot(i,j,k,t) * TEMP(i,j,k,t) )

  ! dew point
  call ATMOS_SATURATION_tdew_liq( DENS(i,j,k,t), TEMP(i,j,k,t), QV(i,j,k,t),       & ! [IN]
                                  Tdew(i,j,k,t), converged       ) ! [OUT]
  ! equivalent potential temperature
  call ATMOS_SATURATION_pote( DENS(i,j,k,t), POTT(i,j,k,t), TEMP(i,j,k,t), QV(i,j,k,t), & ! [IN]
                              POTE(i,j,k,t)                           ) ! [OUT]
  end do
  end do
  end do
  end do


  do t = 1, TA
  do j = 1, JA
  do i = 1, JA
  ! lift parcel
  call ATMOS_ADIABAT_cape( KA, KS, KE, Kstr, &
                           DENS(i,j,KS:KE,t), TEMP(i,j,KS:KE,t), PRES(i,j,KS:KE,t),             & ! [IN]
                           QV(i,j,KS:KE,t), QC(i,j,KS:KE,t), QDRY(i,j,KS:KE,t), Rtot(i,j,KS:KE,t), CPtot(i,j,KS:KE,t),    & ! [IN]
                           CZ, FZ,                       & ! [IN]
                           CAPE(i,j,t), CIN(i,j,t), LCL(i,j,t), LFC(i,j,t), LNB(i,j,t),     & ! [OUT]
                           DENS_p(i,j,KS:KE,t), TEMP_p(i,j,KS:KE,t), BUOY_p(i,j,KS:KE,t), QV_p(i,j,KS:KE,t), & ! [OUT]
                           converged                     ) ! [OUT]
  end do
  end do
  end do


  call SCALE_finalize
  !stop

end subroutine test_scale_adiabat
