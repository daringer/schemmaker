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
      terminal vbias4: electrical;
      terminal gnd: electrical;
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
      
      
      attribute SigDir of vbias1:terminal is "reference";
      attribute SigType of vbias1:terminal is "voltage";
      
      
      attribute SigDir of vdd:terminal is "reference";
      attribute SigType of vdd:terminal is "current";
      attribute SigBias of vdd:terminal is "positive";
      
      attribute SigDir of vbias4:terminal is "reference";
      attribute SigType of vbias4:terminal is "voltage";
      
      
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
      
      
  terminal net1: electrical;
  terminal net2: electrical;
  terminal net3: electrical;
  terminal net4: electrical;
  terminal net5: electrical;
  terminal net6: electrical;
  terminal net7: electrical;
  terminal net8: electrical;

begin


subnet0_subnet0_m1 : entity pmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 2.7e-06,
    W => Wdiff_0,
    Wdiff_0init => 5.14e-05,
    scope => private
)
port map(
     D => net2,
     G => in1,
     S => net1
);
subnet0_subnet0_m2 : entity pmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 2.7e-06,
    W => Wdiff_0,
    Wdiff_0init => 5.14e-05,
    scope => private
)
port map(
     D => net3,
     G => in2,
     S => net1
);
subnet0_subnet0_m3 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => W_0,
    W_0init => 5.575e-05
)
port map(
     D => net1,
     G => vbias1,
     S => vdd
);
subnet0_subnet1_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => Wcursrc_1,
    Wcursrc_1init => 9.4e-06,
    scope => Wprivate,
    symmetry_scope => sym_3
)
port map(
     D => net2,
     G => vbias4,
     S => gnd
);
subnet0_subnet2_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => Wcursrc_1,
    Wcursrc_1init => 9.4e-06,
    scope => Wprivate,
    symmetry_scope => sym_3
)
port map(
     D => net3,
     G => vbias4,
     S => gnd
);
subnet0_subnet3_m1 : entity pmos(behave)
generic map(
    L => L_2,
    L_2init => 3.35e-06,
    W => Wsrc_2,
    Wsrc_2init => 7.415e-05,
    scope => Wprivate,
    symmetry_scope => sym_4
)
port map(
     D => out1,
     G => net2,
     S => vdd
);
subnet0_subnet4_m1 : entity pmos(behave)
generic map(
    L => L_3,
    L_3init => 3.65e-06,
    W => Wsrc_2,
    Wsrc_2init => 7.415e-05,
    scope => Wprivate,
    symmetry_scope => sym_4
)
port map(
     D => out2,
     G => net3,
     S => vdd
);
subnet0_subnet5_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => Wcursrc_3,
    Wcursrc_3init => 8e-07,
    scope => Wprivate,
    symmetry_scope => sym_5
)
port map(
     D => out1,
     G => vbias4,
     S => gnd
);
subnet0_subnet6_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => Wcursrc_3,
    Wcursrc_3init => 8e-07,
    scope => Wprivate,
    symmetry_scope => sym_5
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
     P => net4,
     N => out1
);
subnet1_subnet0_r2 : entity res(behave)
generic map(
    R => 1e+07
)
port map(
     P => net4,
     N => out2
);
subnet1_subnet0_c2 : entity cap(behave)
generic map(
    C => Ccmfb
)
port map(
     P => net7,
     N => vref
);
subnet1_subnet0_c1 : entity cap(behave)
generic map(
    C => Ccmfb
)
port map(
     P => net6,
     N => net4
);
subnet1_subnet0_t1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => W_1,
    W_1init => 6.03e-05
)
port map(
     D => net5,
     G => vbias1,
     S => vdd
);
subnet1_subnet0_t2 : entity pmos(behave)
generic map(
    L => Lcmdiff_0,
    Lcmdiff_0init => 7.9e-06,
    W => Wcmdiff_0,
    Wcmdiff_0init => 4.39e-05,
    scope => private
)
port map(
     D => net7,
     G => vref,
     S => net5
);
subnet1_subnet0_t3 : entity pmos(behave)
generic map(
    L => Lcmdiff_0,
    Lcmdiff_0init => 7.9e-06,
    W => Wcmdiff_0,
    Wcmdiff_0init => 4.39e-05,
    scope => private
)
port map(
     D => net6,
     G => net4,
     S => net5
);
subnet1_subnet0_t4 : entity nmos(behave)
generic map(
    L => Lcm_0,
    Lcm_0init => 7.15e-06,
    W => Wcmfbload_0,
    Wcmfbload_0init => 1.35e-06,
    scope => private
)
port map(
     D => net6,
     G => net6,
     S => gnd
);
subnet1_subnet0_t5 : entity nmos(behave)
generic map(
    L => Lcm_0,
    Lcm_0init => 7.15e-06,
    W => Wcmfbload_0,
    Wcmfbload_0init => 1.35e-06,
    scope => private
)
port map(
     D => net7,
     G => net6,
     S => gnd
);
subnet1_subnet0_t6 : entity nmos(behave)
generic map(
    L => Lcmbias_0,
    Lcmbias_0init => 3.55e-06,
    W => Wcmbias_0,
    Wcmbias_0init => 2.465e-05,
    scope => private
)
port map(
     D => out1,
     G => net7,
     S => gnd
);
subnet1_subnet0_t7 : entity nmos(behave)
generic map(
    L => Lcmbias_0,
    Lcmbias_0init => 3.55e-06,
    W => Wcmbias_0,
    Wcmbias_0init => 2.465e-05,
    scope => private
)
port map(
     D => out2,
     G => net7,
     S => gnd
);
subnet2_subnet0_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => (pfak)*(WBias),
    WBiasinit => 2.22e-05
)
port map(
     D => vbias1,
     G => vbias1,
     S => vdd
);
subnet2_subnet0_m2 : entity pmos(behave)
generic map(
    L => (pfak)*(LBias),
    LBiasinit => 6.15e-06,
    W => (pfak)*(WBias),
    WBiasinit => 2.22e-05
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
    LBiasinit => 6.15e-06,
    W => WBias,
    WBiasinit => 2.22e-05
)
port map(
     D => vbias3,
     G => vbias3,
     S => vbias4
);
subnet2_subnet0_m4 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => WBias,
    WBiasinit => 2.22e-05
)
port map(
     D => vbias2,
     G => vbias3,
     S => net8
);
subnet2_subnet0_m5 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => WBias,
    WBiasinit => 2.22e-05
)
port map(
     D => vbias4,
     G => vbias4,
     S => gnd
);
subnet2_subnet0_m6 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 6.15e-06,
    W => WBias,
    WBiasinit => 2.22e-05
)
port map(
     D => net8,
     G => vbias4,
     S => gnd
);
end simple;
