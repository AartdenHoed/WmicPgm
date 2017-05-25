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
        public ActionResult Load() {
            return View();
        }

        // GET: Future
        public ActionResult Future() {
            TempData["SympaMsg"] = "This function has not yet been implemented.";
            return RedirectToAction("Index");
        }
    }
}