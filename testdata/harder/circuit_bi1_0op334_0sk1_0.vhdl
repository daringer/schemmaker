package STRSYN is
  attribute SigDir : string;
  attribute SigType : string;
  attribute SigBias : string;
end STRSYN;

entity sklp is
  port ( 
      terminal in1: electrical;
      terminal out1: electrical;
      terminal vbias4: electrical;
      terminal gnd: electrical;
      terminal vbias3: electrical;
      terminal vdd: electrical;
      terminal vbias1: electrical;
      terminal vbias2: electrical;
      terminal vref: electrical);
      
end sklp;

architecture simple of sklp is
-- Attributes for Ports
      
      attribute SigDir of in1:terminal is "input";
      attribute SigType of in1:terminal is "voltage";
      
      
      attribute SigDir of out1:terminal is "output";
      attribute SigType of out1:terminal is "voltage";
      
      
      attribute SigDir of vbias4:terminal is "reference";
      attribute SigType of vbias4:terminal is "voltage";
      
      
      attribute SigDir of gnd:terminal is "reference";
      attribute SigType of gnd:terminal is "current";
      attribute SigBias of gnd:terminal is "negative";
      
      attribute SigDir of vbias3:terminal is "reference";
      attribute SigType of vbias3:terminal is "voltage";
      
      
      attribute SigDir of vdd:terminal is "reference";
      attribute SigType of vdd:terminal is "current";
      attribute SigBias of vdd:terminal is "positive";
      
      attribute SigDir of vbias1:terminal is "reference";
      attribute SigType of vbias1:terminal is "voltage";
      
      
      attribute SigDir of vbias2:terminal is "reference";
      attribute SigType of vbias2:terminal is "voltage";
      
      
      attribute SigDir of vref:terminal is "reference";
      attribute SigType of vref:terminal is "current";
      attribute SigBias of vref:terminal is "negative";
      
  terminal net1: electrical;
  terminal net2: electrical;
  terminal net3: electrical;
  terminal net4: electrical;
  terminal net5: electrical;
  terminal net6: electrical;
  terminal net7: electrical;

begin


subnet0_subnet0_subnet0_m1 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 7e-07,
    W => Wdiff_0,
    Wdiff_0init => 2.94e-05,
    scope => private
)
port map(
     D => net2,
     G => net1,
     S => net5
);
subnet0_subnet0_subnet0_m2 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    Ldiff_0init => 7e-07,
    W => Wdiff_0,
    Wdiff_0init => 2.94e-05,
    scope => private
)
port map(
     D => net3,
     G => out1,
     S => net5
);
subnet0_subnet0_subnet0_m3 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => W_0,
    W_0init => 7.635e-05
)
port map(
     D => net5,
     G => vbias4,
     S => gnd
);
subnet0_subnet0_subnet1_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => Wcasc_2,
    Wcasc_2init => 7.215e-05,
    scope => Wprivate,
    symmetry_scope => sym_5
)
port map(
     D => net4,
     G => vbias3,
     S => net2
);
subnet0_subnet0_subnet2_m1 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => Wcasc_2,
    Wcasc_2init => 7.215e-05,
    scope => Wprivate,
    symmetry_scope => sym_5
)
port map(
     D => out1,
     G => vbias3,
     S => net3
);
subnet0_subnet0_subnet3_m1 : entity pmos(behave)
generic map(
    L => Lcm_1,
    Lcm_1init => 1.29e-05,
    W => Wcm_1,
    Wcm_1init => 4.67e-05,
    scope => private
)
port map(
     D => net4,
     G => net4,
     S => vdd
);
subnet0_subnet0_subnet3_m2 : entity pmos(behave)
generic map(
    L => Lcm_1,
    Lcm_1init => 1.29e-05,
    W => Wcmout_1,
    Wcmout_1init => 4.975e-05,
    scope => private
)
port map(
     D => out1,
     G => net4,
     S => vdd
);
subnet0_subnet1_subnet0_m1 : entity pmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => (pfak)*(WBias),
    WBiasinit => 3.55e-06
)
port map(
     D => vbias1,
     G => vbias1,
     S => vdd
);
subnet0_subnet1_subnet0_m2 : entity pmos(behave)
generic map(
    L => (pfak)*(LBias),
    LBiasinit => 1.05e-06,
    W => (pfak)*(WBias),
    WBiasinit => 3.55e-06
)
port map(
     D => vbias2,
     G => vbias2,
     S => vbias1
);
subnet0_subnet1_subnet0_i1 : entity idc(behave)
generic map(
    I => 1.145e-05
)
port map(
     P => vdd,
     N => vbias3
);
subnet0_subnet1_subnet0_m3 : entity nmos(behave)
generic map(
    L => (pfak)*(LBias),
    LBiasinit => 1.05e-06,
    W => WBias,
    WBiasinit => 3.55e-06
)
port map(
     D => vbias3,
     G => vbias3,
     S => vbias4
);
subnet0_subnet1_subnet0_m4 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => WBias,
    WBiasinit => 3.55e-06
)
port map(
     D => vbias2,
     G => vbias3,
     S => net6
);
subnet0_subnet1_subnet0_m5 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => WBias,
    WBiasinit => 3.55e-06
)
port map(
     D => vbias4,
     G => vbias4,
     S => gnd
);
subnet0_subnet1_subnet0_m6 : entity nmos(behave)
generic map(
    L => LBias,
    LBiasinit => 1.05e-06,
    W => WBias,
    WBiasinit => 3.55e-06
)
port map(
     D => net6,
     G => vbias4,
     S => gnd
);
subnet1_subnet0_r1 : entity res(behave)
generic map(
    R => 200000
)
port map(
     P => net7,
     N => in1
);
subnet1_subnet0_r2 : entity res(behave)
generic map(
    R => 603000
)
port map(
     P => net7,
     N => net1
);
subnet1_subnet0_c2 : entity cap(behave)
generic map(
    C => 1.07e-11
)
port map(
     P => net7,
     N => out1
);
subnet1_subnet0_c1 : entity cap(behave)
generic map(
    C => 4e-12
)
port map(
     P => net1,
     N => vref
);
end simple;
