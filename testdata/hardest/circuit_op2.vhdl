package STRSYN is
  attribute SigDir : string;
  attribute SigType : string;
  attribute SigBias : string;
end STRSYN;

entity opfd is
  port ( 
      terminal in1: electrical;
      terminal in2: electrical;
      terminal out1: electrical;
      terminal out2: electrical;
      terminal vbias4: electrical;
      terminal gnd: electrical;
      terminal vdd: electrical;
      terminal vbias1: electrical;
      terminal vref: electrical;
      terminal vbias2: electrical;
      terminal vbias3: electrical);
      
end opfd;

architecture simple of opfd is
-- Attributes for Ports
      
      attribute SigDir of in1:terminal is "input";
      attribute SigType of in1:terminal is "undef";
      
      
      attribute SigDir of in2:terminal is "input";
      attribute SigType of in2:terminal is "undef";
      
      
      attribute SigDir of out1:terminal is "output";
      attribute SigType of out1:terminal is "undef";
      
      
      attribute SigDir of out2:terminal is "output";
      attribute SigType of out2:terminal is "undef";
      
      
      attribute SigDir of vbias4:terminal is "reference";
      attribute SigType of vbias4:terminal is "voltage";
      
      
      attribute SigDir of gnd:terminal is "reference";
      attribute SigType of gnd:terminal is "current";
      attribute SigBias of gnd:terminal is "negative";
      
      attribute SigDir of vdd:terminal is "reference";
      attribute SigType of vdd:terminal is "current";
      attribute SigBias of vdd:terminal is "positive";
      
      attribute SigDir of vbias1:terminal is "reference";
      attribute SigType of vbias1:terminal is "voltage";
      
      
      attribute SigDir of vref:terminal is "reference";
      attribute SigType of vref:terminal is "current";
      attribute SigBias of vref:terminal is "negative";
      
      attribute SigDir of vbias2:terminal is "reference";
      attribute SigType of vbias2:terminal is "voltage";
      
      
      attribute SigDir of vbias3:terminal is "reference";
      attribute SigType of vbias3:terminal is "voltage";
      
      
  terminal net1: electrical;
  terminal net2: electrical;
  terminal net3: electrical;
  terminal net4: electrical;
  terminal net5: electrical;
  terminal net6: electrical;
  terminal net7: electrical;
  terminal net8: electrical;
  terminal net9: electrical;
  terminal net10: electrical;
  terminal net11: electrical;
  terminal net12: electrical;
  terminal net13: electrical;

begin


subnet0_subnet0_m1 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 7.6e-06,
    W => Wdiff_0,
    Wdiff_0init => 6.8e-06,
    scope => private
)
port map(
     D => net1,
     G => in1,
     S => net7
);
subnet0_subnet0_m2 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 7.6e-06,
    W => Wdiff_0,
    Wdiff_0init => 6.8e-06,
    scope => private
)
port map(
     D => net2,
     G => in2,
     S => net7
);
subnet0_subnet0_m3 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => W_0,
    W_0init => 6.79e-05
)
port map(
     D => net7,
     G => vbias4,
     S => gnd
);
subnet0_subnet0_m4 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 7.6e-06,
    W => Wdiff_0,
    Wdiff_0init => 6.8e-06,
    scope => private
)
port map(
     D => net8,
     G => in1,
     S => net7
);
subnet0_subnet0_m5 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 7.6e-06,
    W => Wdiff_0,
    Wdiff_0init => 6.8e-06,
    scope => private
)
port map(
     D => net8,
     G => in2,
     S => net7
);
subnet0_subnet0_m6 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    Lcmdiffp_0init => 8.05e-06,
    W => Wcmdiffp_0,
    Wcmdiffp_0init => 3.5e-06,
    scope => private
)
port map(
     D => net8,
     G => net8,
     S => vdd
);
subnet0_subnet0_m7 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    Lcmdiffp_0init => 8.05e-06,
    W => Wcmdiffp_0,
    Wcmdiffp_0init => 3.5e-06,
    scope => private
)
port map(
     D => net8,
     G => net8,
     S => vdd
);
subnet0_subnet0_m8 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    Lcmdiffp_0init => 8.05e-06,
    W => Wcmdiffp_0,
    Wcmdiffp_0init => 3.5e-06,
    scope => private
)
port map(
     D => net1,
     G => net8,
     S => vdd
);
subnet0_subnet0_m9 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    Lcmdiffp_0init => 8.05e-06,
    W => Wcmdiffp_0,
    Wcmdiffp_0init => 3.5e-06,
    scope => private
)
port map(
     D => net2,
     G => net8,
     S => vdd
);
subnet0_subnet1_m1 : entity pmos(behave)
generic map(
    L => L_2,
    L_2init => 6.15e-06,
    W => Wsrc_1,
    Wsrc_1init => 7.57e-05,
    scope => Wprivate,
    symmetry_scope => sym_3
)
port map(
     D => net3,
     G => net1,
     S => vdd
);
subnet0_subnet2_m1 : entity pmos(behave)
generic map(
    L => L_3,
    L_3init => 3.5e-06,
    W => Wsrc_1,
    Wsrc_1init => 7.57e-05,
    scope => Wprivate,
    symmetry_scope => sym_3
)
port map(
     D => net4,
     G => net2,
     S => vdd
);
subnet0_subnet3_m1 : entity nmos(behave)
generic map(
    L => Lcm_2,
    Lcm_2init => 8.5e-07,
    W => Wcm_2,
    Wcm_2init => 1.925e-05,
    scope => private,
    symmetry_scope => sym_4
)
port map(
     D => net3,
     G => net3,
     S => gnd
);
subnet0_subnet3_m2 : entity nmos(behave)
generic map(
    L => Lcm_2,
    Lcm_2init => 8.5e-07,
    W => Wcmcout_2,
    Wcmcout_2init => 6.135e-05,
    scope => private,
    symmetry_scope => sym_4
)
port map(
     D => net5,
     G => net3,
     S => gnd
);
subnet0_subnet3_c1 : entity cap(behave)
generic map(
    C => C_4,
    symmetry_scope => sym_4
)
port map(
     P => net5,
     N => net3
);
subnet0_subnet4_m1 : entity nmos(behave)
generic map(
    L => Lcm_2,
    Lcm_2init => 8.5e-07,
    W => Wcm_2,
    Wcm_2init => 1.925e-05,
    scope => private,
    symmetry_scope => sym_4
)
port map(
     D => net4,
     G => net4,
     S => gnd
);
subnet0_subnet4_m2 : entity nmos(behave)
generic map(
    L => Lcm_2,
    Lcm_2init => 8.5e-07,
    W => Wcmcout_2,
    Wcmcout_2init => 6.135e-05,
    scope => private,
    symmetry_scope => sym_4
)
port map(
     D => net6,
     G => net4,
     S => gnd
);
subnet0_subnet4_c1 : entity cap(behave)
generic map(
    C => C_5,
    symmetry_scope => sym_4
)
port map(
     P => net6,
     N => net4
);
subnet0_subnet5_m1 : entity pmos(behave)
generic map(
    L => Lcm_3,
    Lcm_3init => 4e-07,
    W => Wcm_3,
    Wcm_3init => 1.49e-05,
    scope => private,
    symmetry_scope => sym_5
)
port map(
     D => net5,
     G => net5,
     S => vdd
);
subnet0_subnet5_m2 : entity pmos(behave)
generic map(
    L => Lcm_3,
    Lcm_3init => 4e-07,
    W => Wcmout_3,
    Wcmout_3init => 7.05e-05,
    scope => private,
    symmetry_scope => sym_5
)
port map(
     D => out1,
     G => net5,
     S => vdd
);
subnet0_subnet6_m1 : entity pmos(behave)
generic map(
    L => Lcm_3,
    Lcm_3init => 4e-07,
    W => Wcm_3,
    Wcm_3init => 1.49e-05,
    scope => private,
    symmetry_scope => sym_5
)
port map(
     D => net6,
     G => net6,
     S => vdd
);
subnet0_subnet6_m2 : entity pmos(behave)
generic map(
    L => Lcm_3,
    Lcm_3init => 4e-07,
    W => Wcmout_3,
    Wcmout_3init => 7.05e-05,
    scope => private,
    symmetry_scope => sym_5
)
port map(
     D => out2,
     G => net6,
     S => vdd
);
subnet0_subnet7_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => Wcursrc_4,
    Wcursrc_4init => 3.35e-06,
    scope => Wprivate,
    symmetry_scope => sym_6
)
port map(
     D => out1,
     G => vbias4,
     S => gnd
);
subnet0_subnet8_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => Wcursrc_4,
    Wcursrc_4init => 3.35e-06,
    scope => Wprivate,
    symmetry_scope => sym_6
)
port map(
     D => out2,
     G => vbias4,
     S => gnd
);
subnet1_subnet0_r1 : entity res(behave)
generic map(
    R => 1e+07
)
port map(
     P => net9,
     N => out1
);
subnet1_subnet0_r2 : entity res(behave)
generic map(
    R => 1e+07
)
port map(
     P => net9,
     N => out2
);
subnet1_subnet0_c2 : entity cap(behave)
generic map(
    C => Ccmfb
)
port map(
     P => net12,
     N => vref
);
subnet1_subnet0_c1 : entity cap(behave)
generic map(
    C => Ccmfb
)
port map(
     P => net11,
     N => net9
);
subnet1_subnet0_t1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => W_1,
    W_1init => 3.585e-05
)
port map(
     D => net10,
     G => vbias1,
     S => vdd
);
subnet1_subnet0_t2 : entity pmos(behave)
generic map(
    L => Lcmdiff_0,
    Lcmdiff_0init => 4.95e-06,
    W => Wcmdiff_0,
    Wcmdiff_0init => 6.32e-05,
    scope => private
)
port map(
     D => net12,
     G => vref,
     S => net10
);
subnet1_subnet0_t3 : entity pmos(behave)
generic map(
    L => Lcmdiff_0,
    Lcmdiff_0init => 4.95e-06,
    W => Wcmdiff_0,
    Wcmdiff_0init => 6.32e-05,
    scope => private
)
port map(
     D => net11,
     G => net9,
     S => net10
);
subnet1_subnet0_t4 : entity nmos(behave)
generic map(
    L => Lcm_0,
    Lcm_0init => 8.5e-06,
    W => Wcmfbload_0,
    Wcmfbload_0init => 2.15e-06,
    scope => private
)
port map(
     D => net11,
     G => net11,
     S => gnd
);
subnet1_subnet0_t5 : entity nmos(behave)
generic map(
    L => Lcm_0,
    Lcm_0init => 8.5e-06,
    W => Wcmfbload_0,
    Wcmfbload_0init => 2.15e-06,
    scope => private
)
port map(
     D => net12,
     G => net11,
     S => gnd
);
subnet1_subnet0_t6 : entity nmos(behave)
generic map(
    L => Lcmbias_0,
    Lcmbias_0init => 1.5e-06,
    W => Wcmbias_0,
    Wcmbias_0init => 3.345e-05,
    scope => private
)
port map(
     D => out1,
     G => net12,
     S => gnd
);
subnet1_subnet0_t7 : entity nmos(behave)
generic map(
    L => Lcmbias_0,
    Lcmbias_0init => 1.5e-06,
    W => Wcmbias_0,
    Wcmbias_0init => 3.345e-05,
    scope => private
)
port map(
     D => out2,
     G => net12,
     S => gnd
);
subnet2_subnet0_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => (pfak)*(WBias),
    WBiasinit => 2.83e-05
)
port map(
     D => vbias1,
     G => vbias1,
     S => vdd
);
subnet2_subnet0_m2 : entity pmos(behave)
generic map(
    L => (pfak)*(LBias),
    LBiasinit => 7.05e-06,
    W => (pfak)*(WBias),
    WBiasinit => 2.83e-05
)
port map(
     D => vbias2,
     G => vbias2,
     S => vbias1
);
subnet2_subnet0_i1 : entity idc(behave)
generic map(
    I => 1.145e-05
)
port map(
     P => vdd,
     N => vbias3
);
subnet2_subnet0_m3 : entity nmos(behave)
generic map(
    L => (pfak)*(LBias),
    LBiasinit => 7.05e-06,
    W => WBias,
    WBiasinit => 2.83e-05
)
port map(
     D => vbias3,
     G => vbias3,
     S => vbias4
);
subnet2_subnet0_m4 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => WBias,
    WBiasinit => 2.83e-05
)
port map(
     D => vbias2,
     G => vbias3,
     S => net13
);
subnet2_subnet0_m5 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => WBias,
    WBiasinit => 2.83e-05
)
port map(
     D => vbias4,
     G => vbias4,
     S => gnd
);
subnet2_subnet0_m6 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 7.05e-06,
    W => WBias,
    WBiasinit => 2.83e-05
)
port map(
     D => net13,
     G => vbias4,
     S => gnd
);
end simple;
