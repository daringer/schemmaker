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
      terminal vbias1: electrical;
      terminal vdd: electrical;
      terminal gnd: electrical;
      terminal vref: electrical;
      terminal vbias2: electrical;
      terminal vbias3: electrical;
      terminal vbias4: electrical);
      
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
      
      
      attribute SigDir of vbias1:terminal is "reference";
      attribute SigType of vbias1:terminal is "voltage";
      
      
      attribute SigDir of vdd:terminal is "reference";
      attribute SigType of vdd:terminal is "current";
      attribute SigBias of vdd:terminal is "positive";
      
      attribute SigDir of gnd:terminal is "reference";
      attribute SigType of gnd:terminal is "current";
      attribute SigBias of gnd:terminal is "negative";
      
      attribute SigDir of vref:terminal is "reference";
      attribute SigType of vref:terminal is "current";
      attribute SigBias of vref:terminal is "negative";
      
      attribute SigDir of vbias2:terminal is "reference";
      attribute SigType of vbias2:terminal is "voltage";
      
      
      attribute SigDir of vbias3:terminal is "reference";
      attribute SigType of vbias3:terminal is "voltage";
      
      
      attribute SigDir of vbias4:terminal is "reference";
      attribute SigType of vbias4:terminal is "voltage";
      
      
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

begin


subnet0_subnet0_m1 : entity pmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 1.7e-06,
    W => Wdiff_0,
    Wdiff_0init => 6.99e-05,
    scope => private
)
port map(
     D => net2,
     G => in1,
     S => net3
);
subnet0_subnet0_m2 : entity pmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 1.7e-06,
    W => Wdiff_0,
    Wdiff_0init => 6.99e-05,
    scope => private
)
port map(
     D => net1,
     G => in2,
     S => net3
);
subnet0_subnet0_m3 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => W_0,
    W_0init => 1.5e-06
)
port map(
     D => net3,
     G => vbias1,
     S => vdd
);
subnet0_subnet1_m1 : entity nmos(behave)
generic map(
    L => Lcm_1,
    Lcm_1init => 1.45e-06,
    W => Wcm_1,
    Wcm_1init => 1.5e-06,
    scope => private,
    symmetry_scope => sym_3
)
port map(
     D => net1,
     G => net1,
     S => gnd
);
subnet0_subnet1_m2 : entity nmos(behave)
generic map(
    L => Lcm_1,
    Lcm_1init => 1.45e-06,
    W => Wcmcout_1,
    Wcmcout_1init => 4.4e-06,
    scope => private,
    symmetry_scope => sym_3
)
port map(
     D => net4,
     G => net1,
     S => gnd
);
subnet0_subnet2_m1 : entity nmos(behave)
generic map(
    L => Lcm_1,
    Lcm_1init => 1.45e-06,
    W => Wcm_1,
    Wcm_1init => 1.5e-06,
    scope => private,
    symmetry_scope => sym_3
)
port map(
     D => net2,
     G => net2,
     S => gnd
);
subnet0_subnet2_m2 : entity nmos(behave)
generic map(
    L => Lcm_1,
    Lcm_1init => 1.45e-06,
    W => Wcmcout_1,
    Wcmcout_1init => 4.4e-06,
    scope => private,
    symmetry_scope => sym_3
)
port map(
     D => net5,
     G => net2,
     S => gnd
);
subnet0_subnet3_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => Wcursrc_2,
    Wcursrc_2init => 1.55e-06,
    scope => Wprivate,
    symmetry_scope => sym_4
)
port map(
     D => net4,
     G => vbias1,
     S => vdd
);
subnet0_subnet4_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => Wcursrc_2,
    Wcursrc_2init => 1.55e-06,
    scope => Wprivate,
    symmetry_scope => sym_4
)
port map(
     D => net5,
     G => vbias1,
     S => vdd
);
subnet0_subnet5_m1 : entity nmos(behave)
generic map(
    L => Lsrc_3,
    Lsrc_3init => 7.5e-07,
    W => Wsrc_3,
    Wsrc_3init => 6.81e-05,
    scope => private,
    symmetry_scope => sym_5
)
port map(
     D => out1,
     G => net4,
     S => gnd
);
subnet0_subnet5_c1 : entity cap(behave)
generic map(
    C => C_2,
    C_2init => 2.461e-12,
    symmetry_scope => sym_5
)
port map(
     P => out1,
     N => net4
);
subnet0_subnet6_m1 : entity nmos(behave)
generic map(
    L => Lsrc_3,
    Lsrc_3init => 7.5e-07,
    W => Wsrc_3,
    Wsrc_3init => 6.81e-05,
    scope => private,
    symmetry_scope => sym_5
)
port map(
     D => out2,
     G => net5,
     S => gnd
);
subnet0_subnet6_c1 : entity cap(behave)
generic map(
    C => C_3,
    C_3init => 2.17e-12,
    symmetry_scope => sym_5
)
port map(
     P => out2,
     N => net5
);
subnet0_subnet7_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => Wcursrc_4,
    Wcursrc_4init => 4.825e-05,
    scope => Wprivate,
    symmetry_scope => sym_6
)
port map(
     D => out1,
     G => vbias1,
     S => vdd
);
subnet0_subnet8_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => Wcursrc_4,
    Wcursrc_4init => 4.825e-05,
    scope => Wprivate,
    symmetry_scope => sym_6
)
port map(
     D => out2,
     G => vbias1,
     S => vdd
);
subnet1_subnet0_r1 : entity res(behave)
generic map(
    R => 1e+07
)
port map(
     P => net6,
     N => out1
);
subnet1_subnet0_r2 : entity res(behave)
generic map(
    R => 1e+07
)
port map(
     P => net6,
     N => out2
);
subnet1_subnet0_c2 : entity cap(behave)
generic map(
    C => Ccmfb
)
port map(
     P => net9,
     N => vref
);
subnet1_subnet0_c1 : entity cap(behave)
generic map(
    C => Ccmfb
)
port map(
     P => net8,
     N => net6
);
subnet1_subnet0_t1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => W_1,
    W_1init => 3.5e-05
)
port map(
     D => net7,
     G => vbias1,
     S => vdd
);
subnet1_subnet0_t2 : entity pmos(behave)
generic map(
    L => Lcmdiff_0,
    Lcmdiff_0init => 1.08e-05,
    W => Wcmdiff_0,
    Wcmdiff_0init => 2.865e-05,
    scope => private
)
port map(
     D => net9,
     G => vref,
     S => net7
);
subnet1_subnet0_t3 : entity pmos(behave)
generic map(
    L => Lcmdiff_0,
    Lcmdiff_0init => 1.08e-05,
    W => Wcmdiff_0,
    Wcmdiff_0init => 2.865e-05,
    scope => private
)
port map(
     D => net8,
     G => net6,
     S => net7
);
subnet1_subnet0_t4 : entity nmos(behave)
generic map(
    L => Lcm_0,
    Lcm_0init => 1.25e-06,
    W => Wcmfbload_0,
    Wcmfbload_0init => 3.55e-06,
    scope => private
)
port map(
     D => net8,
     G => net8,
     S => gnd
);
subnet1_subnet0_t5 : entity nmos(behave)
generic map(
    L => Lcm_0,
    Lcm_0init => 1.25e-06,
    W => Wcmfbload_0,
    Wcmfbload_0init => 3.55e-06,
    scope => private
)
port map(
     D => net9,
     G => net8,
     S => gnd
);
subnet1_subnet0_t6 : entity nmos(behave)
generic map(
    L => Lcmbias_0,
    Lcmbias_0init => 7.45e-06,
    W => Wcmbias_0,
    Wcmbias_0init => 3.345e-05,
    scope => private
)
port map(
     D => out1,
     G => net9,
     S => gnd
);
subnet1_subnet0_t7 : entity nmos(behave)
generic map(
    L => Lcmbias_0,
    Lcmbias_0init => 7.45e-06,
    W => Wcmbias_0,
    Wcmbias_0init => 3.345e-05,
    scope => private
)
port map(
     D => out2,
     G => net9,
     S => gnd
);
subnet2_subnet0_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => (pfak)*(WBias),
    WBiasinit => 1.45e-06
)
port map(
     D => vbias1,
     G => vbias1,
     S => vdd
);
subnet2_subnet0_m2 : entity pmos(behave)
generic map(
    L => (pfak)*(LBias),
    LBiasinit => 3.5e-07,
    W => (pfak)*(WBias),
    WBiasinit => 1.45e-06
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
    LBiasinit => 3.5e-07,
    W => WBias,
    WBiasinit => 1.45e-06
)
port map(
     D => vbias3,
     G => vbias3,
     S => vbias4
);
subnet2_subnet0_m4 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => WBias,
    WBiasinit => 1.45e-06
)
port map(
     D => vbias2,
     G => vbias3,
     S => net10
);
subnet2_subnet0_m5 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => WBias,
    WBiasinit => 1.45e-06
)
port map(
     D => vbias4,
     G => vbias4,
     S => gnd
);
subnet2_subnet0_m6 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 3.5e-07,
    W => WBias,
    WBiasinit => 1.45e-06
)
port map(
     D => net10,
     G => vbias4,
     S => gnd
);
end simple;
