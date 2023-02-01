using NUnit.Framework;
using OpenTap.Plugins.BasicSteps;
using OpenTap;
using System.IO;
using System;

namespace unittest 
{
    public class Tests
    {
        [SetUp]
        public void Setup()
        {
            System.IO.Directory.CreateDirectory("Settings/Bench/Default");

            System.IO.File.Copy("../../bin/Debug/Packages/Python/PythonVisa/test/PythonVisa.xml", "Settings/PythonVisa.xml", true);
            System.IO.File.Copy("../../bin/Debug/Packages/Python/PythonVisa/test/Instruments.xml", "Settings/Bench/Default/Instruments.xml", true);
            System.IO.File.Copy("../../bin/Debug/Packages/Python/PythonVisa/test/simulation_instrument.yaml", "simulation_instrument.yaml", true);
        }

        [Test]
        public void SimulatedIdnTest()
        {
            Console.WriteLine(System.IO.Directory.GetCurrentDirectory());
            var plan = OpenTap.TestPlan.Load("../../bin/Debug/Packages/Python/PythonVisa/test/idn.TapPlan");
            var run = plan.Execute();
            
            
            Assert.AreEqual(Verdict.Pass, run.Verdict);
        }

    }
}
