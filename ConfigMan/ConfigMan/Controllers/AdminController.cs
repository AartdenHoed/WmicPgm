using ConfigMan.Helpers;
using ConfigMan.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace ConfigMan.Controllers
{
    public class AdminController : Controller
    {
        // GET: Admin
        public ActionResult Index()
        {
            ViewBag.SympaMsg = TempData["SympaMsg"];
            return View();
        }
        
        // GET: Load
        // Parameters: Admin/Load
        [HttpGet]
        public ActionResult Load() {

            return View();
        }

        // POST: Load
        // Parameters: Admin/Load/wmicfile=
        [HttpPost]
        public ActionResult Load(string WmicFile)
        {
            ViewBag.SympaMsg = WmicFile;
            ReadWMICfile wmirapport = new ReadWMICfile();
            wmirapport.Wmirapport(WmicFile);
            return View();
        }

        // GET: Future
        public ActionResult Future() {
            TempData["SympaMsg"] = "This function has not yet been implemented.";
            return RedirectToAction("Index");
        }
    }
}