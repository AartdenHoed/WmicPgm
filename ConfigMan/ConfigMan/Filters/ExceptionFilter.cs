using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace ConfigMan.Filters
{
    public class ExceptionFilter : HandleErrorAttribute
    {
    
        public override void OnException(ExceptionContext filterContext)
        {
            string logmsg = "Message: " + filterContext.Exception.Message ;
            Debug.WriteLine(logmsg, "Error Filter Log");
            filterContext.ExceptionHandled = true;
        }
    }
}
       