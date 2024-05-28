Most entries on the individual scheme pages should be fairly self-explanatory.
Below a few additional notes on some special features.

## Ionization potentials

Ionization potentials (IPs) are given on overview pages and on the individual scheme pages. 
All of the IPs have a reference with a given year. 
Most IPs are taken from these two databases:

- [NIST Atomic Spectra Database (NIST ASD)](https://www.nist.gov/pml/atomic-spectra-database){target="_blank"}
- [Grotrian](http://grotrian.nsu.ru/en){target="_blank"}

In these cases, the years given in parentheses are the years when the databases were last accessed.

To report a better IP value,
please raise an [issue](https://github.com/RIMS-Code/rims-code.github.io/issues){target="_blank"}
or get in touch with a
[maintainer](../about/maintainers.md).

## Saturation curve fits

All saturation curves (where wanted) are fit with a first-rate model 
([Letokhov, 1987](https://www.sciencedirect.com/book/9780124443204/laser-photoionization-spectroscopy){target="_blank"}).
In brief, the saturation curve is fit with the equation:

$$N = N_i + N_{max} \cdot \left[1 - \exp \left(- \frac{I}{I_{sat}}\right)\right]$$

Here $N$ is the measured signal, 
$N_i$ the measured signal at zero irradiance, 
$N_{max}$ the maximum signal, 
$I$ the laser irradiance, 
and $I_{sat}$ the saturation irradiance of the transition. 
While this model does not describe real multilevel transitions, 
it provides a semi-quantitative measure of the effectiveness of the schemes.

## Schemes with maximum wavelength for ionization transition

In some cases, 
the ionization transition is not to a specific autoionizing or Rydberg state,
but rather to the IP. 
In these cases, the transition is indicated with a maximum wavelength
and the transition arrow in the scheme diagram is hollow. 
This is to indicate that the exact final state is not known.
