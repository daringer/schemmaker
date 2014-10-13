package STRSYN is
  attribute SigDir : string;
  attribute SigType : string;
  attribute SigBias : string;
end STRSYN;

entity opamp is
  port ( 
      terminal in1: electrical;
      terminal in2: electrical;
      terminal out1: electrical;
      terminal vbias1: electrical;
      terminal vdd: electrical;
      terminal gnd: electrical);
      
end opamp;

architecture simple of opamp is
-- Attributes for Ports
      
      attribute SigDir of in1:terminal is "input";
      attribute SigType of in1:terminal is "voltage";
      
      
      attribute SigDir of in2:terminal is "input";
      attribute SigType of in2:terminal is "voltage";
      
      
      attribute SigDir of out1:terminal is "output";
      attribute SigType of out1:terminal is "voltage";
      
      
      attribute SigDir of vbias1:terminal is "reference";
      attribute SigType of vbias1:terminal is "voltage";
      
      
      attribute SigDir of vdd:terminal is "reference";
      attribute SigType of vdd:terminal is "current";
      attribute SigBias of vdd:terminal is "positive";
      
      attribute SigDir of gnd:terminal is "reference";
      attribute SigType of gnd:terminal is "current";
      attribute SigBias of gnd:terminal is "negative";
      
  terminal net1: electrical;
  terminal net4: electrical;

begin


subnet0_m1 : entity pmos(behave)
generic map(
    L => Ldiff,
    W => Wdiff,
    scope => private
)
port map(
     D => net1,
     G => in1,
     S => net4
);
subnet0_m2 : entity pmos(behave)
generic map(
    L => Ldiff,
    W => Wdiff,
    scope => private
)
port map(
     D => out1,
     G => in2,
     S => net4
);
subnet0_m3 : entity pmos(behave)
generic map(
    L => LBias
)
port map(
     D => net4,
     G => vbias1,
     S => vdd
);
subnet1_m1 : entity nmos(behave)
generic map(
    L => Lcm,
    W => Wcm,
    scope => private
)
port map(
     D => net1,
     G => net1,
     S => gnd
);
subnet1_m2 : entity nmos(behave)
generic map(
    L => Lcm,
    W => Wcmcout,
    scope => private
)
port map(
     D => out1,
     G => net1,
     S => gnd
);
subnet1_c1 : entity cap(behave)
generic map(
    C => Ccurmir,
    scope => private
)
port map(
     P => out1,
     N => net1
);
end simple;
