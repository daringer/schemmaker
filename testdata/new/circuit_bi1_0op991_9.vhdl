package STRSYN is
  attribute SigDir : string;
  attribute SigType : string;
  attribute SigBias : string;
end STRSYN;

entity op is
  port ( 
      terminal in1: electrical;
      terminal in2: electrical;
      terminal out1: electrical;
      terminal vbias4: electrical;
      terminal gnd: electrical;
      terminal vdd: electrical;
      terminal vbias3: electrical;
      terminal vbias1: electrical;
      terminal vbias2: electrical);
      
end op;

architecture simple of op is
-- Attributes for Ports
      
      attribute SigDir of in1:terminal is "input";
      attribute SigType of in1:terminal is "voltage";
      
      
      attribute SigDir of in2:terminal is "input";
      attribute SigType of in2:terminal is "voltage";
      
      
      attribute SigDir of out1:terminal is "output";
      attribute SigType of out1:terminal is "voltage";
      
      
      attribute SigDir of vbias4:terminal is "reference";
      attribute SigType of vbias4:terminal is "voltage";
      
      
      attribute SigDir of gnd:terminal is "reference";
      attribute SigType of gnd:terminal is "current";
      attribute SigBias of gnd:terminal is "negative";
      
      attribute SigDir of vdd:terminal is "reference";
      attribute SigType of vdd:terminal is "current";
      attribute SigBias of vdd:terminal is "positive";
      
      attribute SigDir of vbias3:terminal is "reference";
      attribute SigType of vbias3:terminal is "voltage";
      
      
      attribute SigDir of vbias1:terminal is "reference";
      attribute SigType of vbias1:terminal is "voltage";
      
      
      attribute SigDir of vbias2:terminal is "reference";
      attribute SigType of vbias2:terminal is "voltage";
      
      
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

begin


subnet0_subnet0_m1 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    W => Wdiff_0,
    scope => private
)
port map(
     D => net1,
     G => in1,
     S => net6
);
subnet0_subnet0_m2 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    W => Wdiff_0,
    scope => private
)
port map(
     D => net2,
     G => in2,
     S => net6
);
subnet0_subnet0_m3 : entity nmos(behave)
generic map(
    L => LBias,
    W => W_0
)
port map(
     D => net6,
     G => vbias4,
     S => gnd
);
subnet0_subnet0_m4 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    W => Wdiff_0,
    scope => private
)
port map(
     D => net7,
     G => in1,
     S => net6
);
subnet0_subnet0_m5 : entity nmos(behave)
generic map(
    L => Ldiff_0,
    W => Wdiff_0,
    scope => private
)
port map(
     D => net7,
     G => in2,
     S => net6
);
subnet0_subnet0_m6 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    W => Wcmdiffp_0,
    scope => private
)
port map(
     D => net7,
     G => net7,
     S => vdd
);
subnet0_subnet0_m7 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    W => Wcmdiffp_0,
    scope => private
)
port map(
     D => net7,
     G => net7,
     S => vdd
);
subnet0_subnet0_m8 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    W => Wcmdiffp_0,
    scope => private
)
port map(
     D => net1,
     G => net7,
     S => vdd
);
subnet0_subnet0_m9 : entity pmos(behave)
generic map(
    L => Lcmdiffp_0,
    W => Wcmdiffp_0,
    scope => private
)
port map(
     D => net2,
     G => net7,
     S => vdd
);
subnet0_subnet1_m1 : entity pmos(behave)
generic map(
    L => Lsrc,
    W => Wsrc_2,
    scope => Wprivate,
    symmetry_scope => sym_7
)
port map(
     D => net3,
     G => net1,
     S => vdd
);
subnet0_subnet2_m1 : entity pmos(behave)
generic map(
    L => Lsrc,
    W => Wsrc_2,
    scope => Wprivate,
    symmetry_scope => sym_7
)
port map(
     D => net4,
     G => net2,
     S => vdd
);
subnet0_subnet3_m1 : entity nmos(behave)
generic map(
    L => LBias,
    W => Wcmcasc_3,
    scope => Wprivate,
    symmetry_scope => sym_8
)
port map(
     D => net3,
     G => vbias3,
     S => net8
);
subnet0_subnet3_m2 : entity nmos(behave)
generic map(
    L => Lcm_3,
    W => Wcm_3,
    scope => private,
    symmetry_scope => sym_8
)
port map(
     D => net8,
     G => net3,
     S => gnd
);
subnet0_subnet3_m3 : entity nmos(behave)
generic map(
    L => Lcm_3,
    W => Wcmout_3,
    scope => private,
    symmetry_scope => sym_8
)
port map(
     D => net9,
     G => net3,
     S => gnd
);
subnet0_subnet3_m4 : entity nmos(behave)
generic map(
    L => LBias,
    W => Wcmcasc_3,
    scope => Wprivate,
    symmetry_scope => sym_8
)
port map(
     D => out1,
     G => vbias3,
     S => net9
);
subnet0_subnet4_m1 : entity nmos(behave)
generic map(
    L => LBias,
    W => Wcmcasc_3,
    scope => Wprivate,
    symmetry_scope => sym_8
)
port map(
     D => net4,
     G => vbias3,
     S => net10
);
subnet0_subnet4_m2 : entity nmos(behave)
generic map(
    L => Lcm_3,
    W => Wcm_3,
    scope => private,
    symmetry_scope => sym_8
)
port map(
     D => net10,
     G => net4,
     S => gnd
);
subnet0_subnet4_m3 : entity nmos(behave)
generic map(
    L => Lcm_3,
    W => Wcmout_3,
    scope => private,
    symmetry_scope => sym_8
)
port map(
     D => net11,
     G => net4,
     S => gnd
);
subnet0_subnet4_m4 : entity nmos(behave)
generic map(
    L => LBias,
    W => Wcmcasc_3,
    scope => Wprivate,
    symmetry_scope => sym_8
)
port map(
     D => net5,
     G => vbias3,
     S => net11
);
subnet0_subnet5_m1 : entity pmos(behave)
generic map(
    L => Lcm_1,
    W => Wcm_1,
    scope => private
)
port map(
     D => net5,
     G => net5,
     S => vdd
);
subnet0_subnet5_m2 : entity pmos(behave)
generic map(
    L => Lcm_1,
    W => Wcmout_1,
    scope => private
)
port map(
     D => out1,
     G => net5,
     S => vdd
);
subnet1_subnet0_m1 : entity pmos(behave)
generic map(
    L => LBias,
    W => (pfak)*(WBias)
)
port map(
     D => vbias1,
     G => vbias1,
     S => vdd
);
subnet1_subnet0_m2 : entity pmos(behave)
generic map(
    L => (pfak)*(LBias),
    W => (pfak)*(WBias)
)
port map(
     D => vbias2,
     G => vbias2,
     S => vbias1
);
subnet1_subnet0_i1 : entity idc(behave)
generic map(
    dc => 1.145e-05
)
port map(
     P => vdd,
     N => vbias3
);
subnet1_subnet0_m3 : entity nmos(behave)
generic map(
    L => (pfak)*(LBias),
    W => WBias
)
port map(
     D => vbias3,
     G => vbias3,
     S => vbias4
);
subnet1_subnet0_m4 : entity nmos(behave)
generic map(
    L => LBias,
    W => WBias
)
port map(
     D => vbias2,
     G => vbias3,
     S => net12
);
subnet1_subnet0_m5 : entity nmos(behave)
generic map(
    L => LBias,
    W => WBias
)
port map(
     D => vbias4,
     G => vbias4,
     S => gnd
);
subnet1_subnet0_m6 : entity nmos(behave)
generic map(
    L => LBias,
    W => WBias
)
port map(
     D => net12,
     G => vbias4,
     S => gnd
);
end simple;
