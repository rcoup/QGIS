
/** Raster resample filter */

class QgsRasterResampleFilter : QgsRasterInterface
{
%TypeHeaderCode
#include <qgsrasterresamplefilter.h>
%End

  public:
    QgsRasterResampleFilter( QgsRasterInterface *input = 0 );
    ~QgsRasterResampleFilter();

    virtual QgsRasterResampleFilter * clone() const /Factory/;

    int bandCount() const;

    Qgis::DataType dataType( int bandNo ) const;

    bool setInput( QgsRasterInterface* input );

    QgsRasterBlock *block( int bandNo, const QgsRectangle &extent, int width, int height, QgsRasterBlockFeedback* feedback = nullptr ) /Factory/;

    /** Set resampler for zoomed in scales. Takes ownership of the object*/
    void setZoomedInResampler( QgsRasterResampler* r /Transfer/ );
    const QgsRasterResampler* zoomedInResampler() const;

    /** Set resampler for zoomed out scales. Takes ownership of the object*/
    void setZoomedOutResampler( QgsRasterResampler* r /Transfer/ );
    const QgsRasterResampler* zoomedOutResampler() const;

    void setMaxOversampling( double os );
    double maxOversampling() const;

    void writeXml( QDomDocument& doc, QDomElement& parentElem ) const;

    /** Sets base class members from xml. Usually called from create() methods of subclasses*/
    void readXml( const QDomElement& filterElem );
};

