using System;
using System.Collections.Generic;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Linq;
using System.Web;
using ConfigMan.Controllers;
using System.Web.Mvc;

namespace ConfigMan.UnitTests
{
    [TestClass]
    public class TestScripts
    {
        [TestMethod]
        public void TestComputersController()
        {
            var controller = new ComputersController();
            var result = controller.Details(0) as ViewResult;
            Assert.AreEqual("Index", result.ViewName);

        }
    }
}