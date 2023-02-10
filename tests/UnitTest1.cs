namespace tests;

using System;
using System.IO;

using OpenTap;
using OpenTap.Plugins.BasicSteps;

public class Tests
{
    [SetUp]
    public void Setup()
    {
        Console.WriteLine("Current working directory is: " + System.IO.Directory.GetCurrentDirectory());
        
        System.IO.Directory.CreateDirectory("./Settings/Bench/Default");

        System.IO.File.Copy("../../../idn.TapPlan", "./idn.TapPlan", true);
        System.IO.File.Copy("../../../PythonVisa.xml", "./Settings/PythonVisa.xml", true);
        System.IO.File.Copy("../../../Instruments.xml", "./Settings/Bench/Default/Instruments.xml", true);
        System.IO.File.Copy("../../../simulation_instrument.yaml", "./simulation_instrument.yaml", true);
    }

    [Test]
    public void SimulatedIdnTest()
    {
        //System.IO.Directory.SetCurrentDirectory("../../../../bin");
        Console.WriteLine(System.IO.Directory.GetCurrentDirectory());
        
        //OpenTap.EngineSettings.LoadWorkingDirectory("../../../../bin");
        var plan = OpenTap.TestPlan.Load("idn.TapPlan");
        var run = plan.Execute();
        
        
        Assert.AreEqual(Verdict.Pass, run.Verdict);
    }
}