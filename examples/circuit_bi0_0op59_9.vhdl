library IEEE;
use IEEE.std_logic_1164.all;

library IEEE_proposed;
use IEEE_proposed.electrical_systems.all;
use IEEE_proposed.mechanical_systems.all;
use IEEE_proposed.fluidic_systems.all;
use IEEE_proposed.thermal_systems.all;
use IEEE_proposed.radiant_systems.all;

package STRSYN is
  attribute SigDir : string;
  attribute Z : string;
  attribute SigType : string;
  attribute BiasDir : string;
end STRSYN;

entity speci is
  port ( 
      terminal inp1: electrical;
      terminal inp2: electrical;
      terminal outp: electrical;
      terminal vdd: electrical;
      terminal gnd: electrical;
      terminal vbias1: electrical;
      terminal vbias2: electrical;
      terminal vbias3: electrical;
      terminal vbias4: electrical;
       );
end speci;

architecture simple of speci is
-- Attributes for Ports
      
      attribute 'SigDir' of inp1:terminal is "input";
      attribute 'Z' of inp1:terminal is "high";
      attribute 'SigType' of inp1:terminal is "voltage";
      
      
      attribute 'SigDir' of inp2:terminal is "input";
      attribute 'Z' of inp2:terminal is "high";
      attribute 'SigType' of inp2:terminal is "voltage";
      
      
      attribute 'SigDir' of outp:terminal is "output";
      attribute 'Z' of outp:terminal is "high";
      attribute 'SigType' of outp:terminal is "voltage";
      
      
      attribute 'SigDir' of vdd:terminal is "reference";
      attribute 'Z' of vdd:terminal is "low";
      attribute 'SigType' of vdd:terminal is "current";
      attribute 'BiasDir' of vdd:terminal is "positive";
      
      attribute 'SigDir' of gnd:terminal is "reference";
      attribute 'Z' of gnd:terminal is "low";
      attribute 'SigType' of gnd:terminal is "current";
      attribute 'BiasDir' of gnd:terminal is "negative";
      
      attribute 'SigDir' of vbias1:terminal is "reference";
      attribute 'Z' of vbias1:terminal is "high";
      attribute 'SigType' of vbias1:terminal is "voltage";
      
      
      attribute 'SigDir' of vbias2:terminal is "reference";
      attribute 'Z' of vbias2:terminal is "high";
      attribute 'SigType' of vbias2:terminal is "voltage";
      
      
      attribute 'SigDir' of vbias3:terminal is "reference";
      attribute 'Z' of vbias3:terminal is "high";
      attribute 'SigType' of vbias3:terminal is "voltage";
      
      
      attribute 'SigDir' of vbias4:terminal is "reference";
      attribute 'Z' of vbias4:terminal is "high";
      attribute 'SigType' of vbias4:terminal is "voltage";
      
      
  terminal net1: electrical;
  terminal net2: electrical;
  terminal net3: electrical;
  terminal net4: electrical;
  terminal net5: electrical;
  terminal net6: electrical;
  terminal net7: electrical;

begin

-- Constraints
-- hierarchie_subnet0_subnet0_m1_W = hierarchie_subnet0_subnet0_Wdiff
-- hierarchie_subnet0_subnet0_m1_L = hierarchie_subnet0_subnet0_Ldiff
-- hierarchie_subnet0_subnet0_m1_DW = hierarchie_subnet0_subnet0_Wdiff
-- hierarchie_subnet0_subnet0_m1_DL = hierarchie_subnet0_subnet0_Ldiff
-- hierarchie_subnet0_subnet0_m1_scope = hierarchie_subnet0_subnet0_private
-- hierarchie_subnet0_subnet0_m2_W = hierarchie_subnet0_subnet0_Wdiff
-- hierarchie_subnet0_subnet0_m2_L = hierarchie_subnet0_subnet0_Ldiff
-- hierarchie_subnet0_subnet0_m2_DW = hierarchie_subnet0_subnet0_Wdiff
-- hierarchie_subnet0_subnet0_m2_DL = hierarchie_subnet0_subnet0_Ldiff
-- hierarchie_subnet0_subnet0_m2_scope = hierarchie_subnet0_subnet0_private
-- hierarchie_subnet0_subnet1_m1_L = hierarchie_subnet0_subnet1_Lcmup
-- hierarchie_subnet0_subnet1_m1_DL = hierarchie_subnet0_subnet1_Lcmtop
-- hierarchie_subnet0_subnet1_m1_scope = hierarchie_subnet0_subnet1_private
-- hierarchie_subnet0_subnet1_m2_L = hierarchie_subnet0_subnet1_Lcmact
-- hierarchie_subnet0_subnet1_m2_DL = hierarchie_subnet0_subnet1_Lcmbot
-- hierarchie_subnet0_subnet1_m2_scope = hierarchie_subnet0_subnet1_private
-- hierarchie_subnet0_subnet1_m3_L = hierarchie_subnet0_subnet1_Lcmact
-- hierarchie_subnet0_subnet1_m3_DL = hierarchie_subnet0_subnet1_Lcmbot
-- hierarchie_subnet0_subnet1_m3_scope = hierarchie_subnet0_subnet1_private
-- hierarchie_subnet0_subnet1_m4_L = hierarchie_subnet0_subnet1_Lcmup
-- hierarchie_subnet0_subnet1_m4_DL = hierarchie_subnet0_subnet1_Lcmtop
-- hierarchie_subnet0_subnet1_m4_scope = hierarchie_subnet0_subnet1_private
-- hierarchie_subnet1_subnet0_i1_option = hierarchie_subnet1_subnet0_stay
-- hierarchie_subnet1_subnet0_m1_DW = hierarchie_subnet1_subnet0_pfakTIMESWBias
-- hierarchie_subnet1_subnet0_m1_DL = hierarchie_subnet1_subnet0_LBias
-- hierarchie_subnet1_subnet0_m2_DW = hierarchie_subnet1_subnet0_pfakTIMESWBias
-- hierarchie_subnet1_subnet0_m2_DL = hierarchie_subnet1_subnet0_LBias
-- hierarchie_subnet1_subnet0_m3_DW = hierarchie_subnet1_subnet0_WBias
-- hierarchie_subnet1_subnet0_m3_DL = hierarchie_subnet1_subnet0_LBias
-- hierarchie_subnet1_subnet0_m4_DW = hierarchie_subnet1_subnet0_WBias
-- hierarchie_subnet1_subnet0_m4_DL = hierarchie_subnet1_subnet0_LBias
-- hierarchie_subnet1_subnet0_m5_DW = hierarchie_subnet1_subnet0_WBias
-- hierarchie_subnet1_subnet0_m5_DL = hierarchie_subnet1_subnet0_LBias
-- hierarchie_subnet1_subnet0_m6_DW = hierarchie_subnet1_subnet0_WBias
-- hierarchie_subnet1_subnet0_m6_DL = hierarchie_subnet1_subnet0_LBias


subnet0_subnet0_m1 : entity work.basic_pmos(behave)
port map(
     D => outp,
     G => inp1,
     S => net1
);
subnet0_subnet0_m2 : entity work.basic_pmos(behave)
port map(
     D => net4,
     G => inp2,
     S => net1
);
subnet0_subnet0_i2 : entity work.basic_i_constant(ideal)
port map(
     pos => vdd,
     neg => net1
);
subnet0_subnet1_m1 : entity work.basic_nmos(behave)
port map(
     D => net4,
     G => net4,
     S => net2
);
subnet0_subnet1_m2 : entity work.basic_nmos(behave)
port map(
     D => net2,
     G => net2,
     S => gnd
);
subnet0_subnet1_m3 : entity work.basic_nmos(behave)
port map(
     D => net3,
     G => net2,
     S => gnd
);
subnet0_subnet1_m4 : entity work.basic_nmos(behave)
port map(
     D => net5,
     G => net4,
     S => net3
);
subnet0_subnet2_m1 : entity work.basic_pmos(behave)
port map(
     D => net5,
     G => net5,
     S => net6
);
subnet0_subnet3_m1 : entity work.basic_pmos(behave)
port map(
     D => net6,
     G => net6,
     S => outp
);
subnet1_subnet0_m1 : entity work.basic_pmos(behave)
port map(
     D => vbias1,
     G => vbias1,
     S => vdd
);
subnet1_subnet0_m2 : entity work.basic_pmos(behave)
port map(
     D => vbias2,
     G => vbias2,
     S => vbias1
);
subnet1_subnet0_i1 : entity work.basic_i_constant(ideal)
port map(
     pos => vdd,
     neg => vbias3
);
subnet1_subnet0_m3 : entity work.basic_nmos(behave)
port map(
     D => vbias3,
     G => vbias3,
     S => vbias4
);
subnet1_subnet0_m4 : entity work.basic_nmos(behave)
port map(
     D => vbias2,
     G => vbias3,
     S => net7
);
subnet1_subnet0_m5 : entity work.basic_nmos(behave)
port map(
     D => vbias4,
     G => vbias4,
     S => gnd
);
subnet1_subnet0_m6 : entity work.basic_nmos(behave)
port map(
     D => net7,
     G => vbias4,
     S => gnd
);
end simple;
